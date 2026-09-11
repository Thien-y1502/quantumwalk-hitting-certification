from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
import json, math, hashlib, platform, sys, time
import numpy as np
import pandas as pd
import networkx as nx
from scipy import sparse
from scipy.sparse import linalg as spla

from .core import (lazy_random_walk_objects, dirichlet_objects, global_spectral_gap,
                   smallest_eigenvalue_spd, reference_hitting_time, cg_certificate,
                   proposal_h_from_kx)
from .graphs import make_graph, choose_mark, make_cubic_instance
from .rooted import rooted_congestion, best_of_randomized_forests
from .rational import exact_validate_half_lazy_graph, rooted_rho_fraction_half_lazy


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def environment_info() -> Dict[str, object]:
    import scipy, networkx, pandas, matplotlib
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__, "scipy": scipy.__version__, "networkx": networkx.__version__,
        "pandas": pandas.__version__, "matplotlib": matplotlib.__version__,
    }


def run_benchmark(cfg: Dict[str, object], outdir: Path) -> pd.DataFrame:
    rows=[]
    families = cfg["families"]
    sizes = cfg["sizes"]
    policies = cfg["mark_policies"]
    random_seeds = cfg["random_graph_seeds"]
    deterministic = set(cfg["deterministic_families"])
    for family in families:
        seeds = [0] if family in deterministic else random_seeds
        for n_req in sizes:
            for gseed in seeds:
                G, meta = make_graph(family, n_req, gseed)
                obj = lazy_random_walk_objects(G)
                delta = global_spectral_gap(obj)
                for pidx, policy in enumerate(policies):
                    mark = choose_mark(G, policy, gseed, pidx)
                    M,U,K,b,Z,A = dirichlet_objects(obj, [mark])
                    piM = float(obj.pi[obj.node_to_idx[mark]])
                    ell_gap = max(delta*piM, 1e-15)
                    rooted = rooted_congestion(G,obj,[mark])
                    ell_root = rooted.floor
                    multi = best_of_randomized_forests(G,obj,[mark], repeats=int(cfg["multi_forest_repeats"]),
                                                       seed=cfg["master_seed"]+100003*gseed+97*pidx+n_req,
                                                       jitter=float(cfg["multi_forest_jitter"]))
                    ell_multi = multi.floor
                    ell_ref = smallest_eigenvalue_spd(K)
                    floors = {
                        "reference_dirichlet": ell_ref,
                        "global_gap_mass": ell_gap,
                        "marked_rooted": ell_root,
                        "hybrid_max": max(ell_gap,ell_root),
                        "multi_forest": max(ell_gap,ell_multi),
                    }
                    Href, solve_resid = reference_hitting_time(obj,[mark])
                    for fname,ell in floors.items():
                        cert = cg_certificate(K,b,ell,float(cfg["relative_width_tolerance"]),int(cfg["cg_maxiter"]))
                        coverage = (cert.lower <= Href*(1+1e-9)) and (cert.upper+1e-9*max(1.0,Href) >= Href)
                        rows.append({
                            "family":family,"requested_n":n_req,"realized_n":G.number_of_nodes(),"graph_seed":gseed,
                            "policy":policy,"mark":mark,"floor_source":fname,"floor":ell,"delta":delta,"pi_mark":piM,
                            "rho_root":rooted.rho,"rho_multi":multi.rho,"H_ref":Href,"solve_rel_residual":solve_resid,
                            "lower":cert.lower,"upper":cert.upper,"rel_width":cert.width,"iterations":cert.iterations,
                            "converged":cert.converged,"coverage":coverage,
                            "interval_looseness":cert.upper/Href,
                            "floor_upper_bound":1.0/ell,
                            "floor_bound_looseness":1.0/(ell*Href),
                        })
    df=pd.DataFrame(rows)
    outdir.mkdir(parents=True,exist_ok=True)
    df.to_csv(outdir/"benchmark_runs.csv",index=False)
    return df


def benchmark_summary(df: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    order=["reference_dirichlet","global_gap_mass","marked_rooted","hybrid_max","multi_forest"]
    ag=[]
    for f in order:
        s=df[df.floor_source==f]
        ag.append({"floor_source":f,"coverage":s.coverage.mean(),"convergence":s.converged.mean(),
                   "median_width":s.rel_width.median(),"p90_width":s.rel_width.quantile(.9),
                   "median_floor_bound_looseness":s.floor_bound_looseness.median(),
                   "p90_floor_bound_looseness":s.floor_bound_looseness.quantile(.9),
                   "median_interval_looseness":s.interval_looseness.median()})
    aggregate=pd.DataFrame(ag)
    piv=df.pivot_table(index=["family","requested_n","realized_n","graph_seed","policy","mark"],
                       columns="floor_source",values="floor_bound_looseness").reset_index()
    piv["rooted_gain"]=piv["global_gap_mass"]/piv["marked_rooted"]
    piv["multi_gain_over_rooted"]=piv["marked_rooted"]/piv["multi_forest"]
    fam=[]
    for family,g in piv.groupby("family"):
        fam.append({"family":family,
                    "global_gap_mass":g.global_gap_mass.median(),"marked_rooted":g.marked_rooted.median(),
                    "multi_forest":g.multi_forest.median(),"reference_dirichlet":g.reference_dirichlet.median(),
                    "paired_rooted_gain":g.rooted_gain.median(),"paired_multi_gain_over_rooted":g.multi_gain_over_rooted.median()})
    family=pd.DataFrame(fam)
    return aggregate,family,piv


def run_cubic(cfg: Dict[str,object], outdir: Path) -> pd.DataFrame:
    rows=[]
    for m in cfg["cubic_core_sizes"]:
        for seed in cfg["cubic_seeds"]:
            G,a,z,meta=make_cubic_instance(int(m),int(seed))
            obj=lazy_random_walk_objects(G)
            Ha,ra=reference_hitting_time(obj,[a]); Hz,rz=reference_hitting_time(obj,[z])
            rows.append({**meta,"seed":seed,"easy_target":a,"hard_target":z,"H_easy":Ha,"H_hard":Hz,
                         "ratio":Hz/Ha,"easy_residual":ra,"hard_residual":rz})
    df=pd.DataFrame(rows); df.to_csv(outdir/"cubic_runs.csv",index=False)
    return df


def run_fixed_proposal_ablation(cfg: Dict[str,object], outdir: Path) -> pd.DataFrame:
    rows=[]
    # Use one representative middle-size instance from each family.
    n=int(cfg["sizes"][len(cfg["sizes"])//2])
    for fi,family in enumerate(cfg["families"]):
        seed=0
        G,_=make_graph(family,n,seed)
        obj=lazy_random_walk_objects(G); delta=global_spectral_gap(obj)
        mark=choose_mark(G,"last",seed,1)
        M,U,K,b,Z,A=dirichlet_objects(obj,[mark])
        root=rooted_congestion(G,obj,[mark]); multi=best_of_randomized_forests(G,obj,[mark],repeats=int(cfg["multi_forest_repeats"]),seed=123+fi)
        ell_gap=delta*obj.pi[obj.node_to_idx[mark]]; ell_root=root.floor; ell_multi=multi.floor; ell_ref=smallest_eigenvalue_spd(K)
        # Freeze the CG proposal after a fixed number of iterations. The CG iterate itself does not depend on the floor.
        cert=cg_certificate(K,b,ell_ref,rel_width_tol=-1.0,maxiter=int(cfg["fixed_proposal_iterations"]))
        x=cert.x; L=float(b@x); r=b-K@x; r2=float(r@r)
        Href,_=reference_hitting_time(obj,[mark])
        for name,ell in [("global_gap_mass",ell_gap),("marked_rooted",ell_root),("multi_forest",max(ell_gap,ell_multi)),("reference_dirichlet",ell_ref)]:
            Ubd=L+r2/ell
            rows.append({"family":family,"N":G.number_of_nodes(),"mark":mark,"floor_source":name,"floor":ell,
                         "frozen_lower":L,"frozen_upper":Ubd,"correction":r2/ell,"H_ref":Href,"looseness":Ubd/Href})
    df=pd.DataFrame(rows); df.to_csv(outdir/"fixed_proposal_ablation.csv",index=False); return df


def run_bad_proposal(cfg: Dict[str,object], outdir: Path) -> pd.DataFrame:
    rows=[]
    # Small instances keep exact-rational validation tractable across all noise levels.
    cases=[("path",32,0,"last"),("barbell",20,0,"last")]
    noise_levels=cfg["bad_proposal_noise"]
    for ci,(family,n,seed,policy) in enumerate(cases):
        G,_=make_graph(family,n,seed); obj=lazy_random_walk_objects(G); mark=choose_mark(G,policy,seed,1)
        M,U,K,b,Z,A=dirichlet_objects(obj,[mark]); root=rooted_congestion(G,obj,[mark])
        x=spla.spsolve(K.tocsc(),b); piu=obj.pi[U]; h=proposal_h_from_kx(np.asarray(x),piu,Z)
        Href,_=reference_hitting_time(obj,[mark]); rng=np.random.default_rng(int(cfg["master_seed"])+ci)
        direction=rng.normal(size=len(h)); direction/=np.linalg.norm(direction)
        scale=max(np.linalg.norm(h),1.0)
        from .rational import rooted_rho_fraction_half_lazy
        rhoF=rooted_rho_fraction_half_lazy(G,mark,root.parent)
        for sigma in noise_levels:
            y=np.asarray(h)+float(sigma)*scale*direction
            ex=exact_validate_half_lazy_graph(G,mark,y,rhoF)
            lo=float(ex["lower"]); up=float(ex["upper"]); width=float(ex["width"])
            rows.append({"family":family,"N":G.number_of_nodes(),"mark":mark,"sigma":sigma,"H_ref":Href,
                         "lower":lo,"upper":up,"width":width,"relative_width":width/max(lo,1e-300),
                         "width_over_H":width/max(Href,1e-300),
                         "contains_reference": (lo-1e-10*max(1.0,abs(Href)) <= Href <= up+1e-10*max(1.0,abs(Href))),
                         "penalty":float(ex["penalty"])})
    df=pd.DataFrame(rows); df.to_csv(outdir/"bad_proposal_exact.csv",index=False); return df



def run_exact_cases(cfg: Dict[str,object], outdir: Path) -> pd.DataFrame:
    """Evaluate the selected exact-rational validation cases."""
    cases=[]
    G,_=make_graph("path",32,0); cases.append(("Path",G,31))
    G,_=make_graph("barbell",20,0); cases.append(("Barbell",G,19))
    for m in [16,64,256,1024]:
        G,a,z,meta=make_cubic_instance(m,0); cases.append((f"Cubic hard m={m}",G,z))
    rows=[]
    for name,G,mark in cases:
        obj=lazy_random_walk_objects(G); M,U,K,b,Z,A=dirichlet_objects(obj,[mark])
        x=spla.spsolve(K.tocsc(),b); y=proposal_h_from_kx(np.asarray(x),obj.pi[U],Z)
        root=rooted_congestion(G,obj,[mark]); rhoF=rooted_rho_fraction_half_lazy(G,mark,root.parent)
        ex=exact_validate_half_lazy_graph(G,mark,y,rhoF); Href,_=reference_hitting_time(obj,[mark])
        rows.append({"case":name,"N":G.number_of_nodes(),"rooted_congestion":float(rhoF),"H_ref":Href,
                     "exact_lower":float(ex["lower"]),"exact_upper":float(ex["upper"]),"exact_width":float(ex["width"])})
    df=pd.DataFrame(rows); df.to_csv(outdir.parent/"tables"/"exact_rational_cases.csv",index=False); return df

def write_summaries(outdir: Path, benchmark: pd.DataFrame, cubic: pd.DataFrame,
                    fixed: pd.DataFrame, bad: pd.DataFrame):
    agg,fam,piv=benchmark_summary(benchmark)
    agg.to_csv(outdir.parent/"tables"/"aggregate_certificate_summary.csv",index=False)
    fam.to_csv(outdir.parent/"tables"/"family_certificate_summary.csv",index=False)
    piv.to_csv(outdir.parent/"tables"/"paired_evaluations.csv",index=False)
    cubic_summary=cubic.groupby("N").ratio.agg(["min","median","max"]).reset_index()
    cubic_summary.to_csv(outdir.parent/"tables"/"cubic_summary.csv",index=False)
    # Machine-readable run summary.
    audit={
      "benchmark_evaluations": int(len(piv)),
      "certificate_runs": int(len(benchmark)),
      "rooted_improves_count": int((piv.rooted_gain>1).sum()),
      "rooted_improves_fraction": float((piv.rooted_gain>1).mean()),
      "multi_improves_over_rooted_count": int((piv.multi_gain_over_rooted>1+1e-12).sum()),
      "multi_improves_over_rooted_fraction": float((piv.multi_gain_over_rooted>1+1e-12).mean()),
      "max_linear_residual_cubic": float(cubic[["easy_residual","hard_residual"]].to_numpy().max()),
      "bad_proposal_all_contain": bool(bad.contains_reference.all()),
      "environment": environment_info(),
    }
    (outdir.parent/"audits"/"run_audit.json").write_text(json.dumps(audit,indent=2,sort_keys=True),encoding="utf-8")
    return agg,fam,piv,cubic_summary,audit
