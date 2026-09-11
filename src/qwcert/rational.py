from __future__ import annotations
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple
import math
import numpy as np
import networkx as nx


def F(x) -> Fraction:
    if isinstance(x, Fraction): return x
    if isinstance(x, (int, np.integer)): return Fraction(int(x), 1)
    if isinstance(x, float): return Fraction.from_float(float(x))
    return Fraction(x)


def exact_validate_half_lazy_graph(G: nx.Graph, mark: int, y_float: Sequence[float], rho: Fraction) -> Dict[str, object]:
    """Exact-rational Theorem 7 validator for one-half-lazy unweighted graph.

    The proposal is interpreted as the exact dyadic rational represented by
    each binary64 value.  ell=1/rho uses an exact rational rooted floor.
    """
    nodes = sorted(G.nodes())
    U_nodes = [u for u in nodes if u != mark]
    pos = {u:i for i,u in enumerate(U_nodes)}
    m = G.number_of_edges()
    deg = {u:G.degree(u) for u in nodes}
    pi = {u:Fraction(deg[u], 2*m) for u in nodes}
    Z = sum((pi[u] for u in U_nodes), Fraction(0,1))
    y = [Fraction.from_float(float(v)) for v in y_float]
    if len(y) != len(U_nodes):
        raise ValueError("proposal length mismatch")
    # Ay = y - P_UU y.  P_uu has self 1/2 and neighbor 1/(2deg[u]).
    Ay: List[Fraction] = []
    for u in U_nodes:
        i = pos[u]
        val = y[i] - Fraction(1,2)*y[i]
        step = Fraction(1, 2*deg[u])
        for v in G.neighbors(u):
            if v == mark: continue
            val -= step * y[pos[v]]
        Ay.append(val)
    one_y = sum((pi[u] * y[pos[u]] for u in U_nodes), Fraction(0,1))
    yAy = sum((pi[u] * y[pos[u]] * Ay[pos[u]] for u in U_nodes), Fraction(0,1))
    L = (2*one_y - yAy) / Z
    s = [Fraction(1,1) - Ay[i] for i in range(len(U_nodes))]
    s2 = sum((pi[u] * s[pos[u]] * s[pos[u]] for u in U_nodes), Fraction(0,1))
    ell = Fraction(1,1) / rho
    penalty = s2 / (Z * ell)
    lower = max(Fraction(0,1), L)
    upper = L + penalty
    return {
        "lower": lower, "upper": upper, "width": upper-lower,
        "L": L, "penalty": penalty, "Z": Z, "rho": rho, "ell": ell,
        "residual_norm_sq_pi": s2,
    }


def rooted_rho_fraction_half_lazy(G: nx.Graph, mark: int, parent: Dict[int, int|None]) -> Fraction:
    """Recompute rho exactly for a supplied rooted forest."""
    nodes = sorted(G.nodes())
    m = G.number_of_edges()
    deg = {u:G.degree(u) for u in nodes}
    pi = {u:Fraction(deg[u], 2*m) for u in nodes}
    qinv = Fraction(4*m, 1)
    depth = {mark:0}
    pending = set(nodes) - {mark}
    while pending:
        progressed = False
        for u in list(pending):
            p = parent[u]
            if p is None:
                raise RuntimeError("bad parent")
            if p in depth:
                depth[u] = depth[p] + 1
                pending.remove(u)
                progressed = True
        if not progressed:
            raise RuntimeError("parent map contains a cycle or disconnected component")
    own = {u: pi[u]*qinv*depth[u] for u in nodes}
    sub = dict(own)
    for u in sorted(nodes, key=lambda x:(depth[x],x), reverse=True):
        if u == mark: continue
        sub[parent[u]] += sub[u]
    loads = [sub[u] for u in nodes if u != mark]
    return max(loads) if loads else Fraction(0,1)
