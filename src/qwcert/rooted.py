from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import heapq
import numpy as np
import networkx as nx
from .core import ChainObjects


@dataclass
class RootedResult:
    rho: float
    floor: float
    parent: Dict[int, Optional[int]]
    distance: Dict[int, float]
    edge_loads: Dict[Tuple[int, int], float]


def _canonical_edge(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a < b else (b, a)


def rooted_congestion(G: nx.Graph, obj: ChainObjects, marks: Iterable[int],
                      perturb: Optional[Dict[Tuple[int, int], float]] = None) -> RootedResult:
    """Compute rho_M for a deterministic marked-rooted shortest-resistance forest.

    For the half-lazy simple random walk on an unweighted graph, Q(e)=1/(4|E|)
    for every undirected edge.  Optional positive perturbations alter path choice
    but not certificate validity: every selected path system is admissible.
    """
    marks = sorted(set(marks))
    Mset = set(marks)
    if not Mset or len(Mset) == G.number_of_nodes():
        raise ValueError("marked set must be nonempty and proper")
    qinv = float(4 * G.number_of_edges())
    dist = {u: float("inf") for u in G.nodes()}
    parent: Dict[int, Optional[int]] = {u: None for u in G.nodes()}
    heap = []
    for m in marks:
        dist[m] = 0.0
        heapq.heappush(heap, (0.0, m))
    # Multi-source Dijkstra with deterministic tie break by parent/node label.
    while heap:
        du, u = heapq.heappop(heap)
        if du != dist[u]:
            continue
        for v in sorted(G.neighbors(u)):
            e = _canonical_edge(u, v)
            factor = 1.0 if perturb is None else perturb.get(e, 1.0)
            w = qinv * factor
            nd = du + w
            # parent[v] points one step toward a root (u is already settled/closer)
            if nd < dist[v] - 1e-12 or (abs(nd - dist[v]) <= 1e-12 and (parent[v] is None or u < parent[v])):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    # For validity rho uses the *unperturbed* resistance length of selected paths.
    # Count number of edges to root via parent pointers.
    depth: Dict[int, int] = {m: 0 for m in marks}
    for u in sorted(G.nodes(), key=lambda z: (dist[z], z)):
        if u in Mset:
            continue
        p = parent[u]
        if p is None or p not in depth:
            raise RuntimeError("forest does not reach mark or parent order is invalid")
        depth[u] = 1 + depth[p]
    idx = obj.node_to_idx
    own = {u: float(obj.pi[idx[u]] * (qinv * depth[u])) for u in G.nodes()}
    subtree = dict(own)
    # Descending depth accumulates load into parent.
    for u in sorted(G.nodes(), key=lambda z: (depth[z], z), reverse=True):
        if u in Mset:
            continue
        p = parent[u]
        subtree[p] += subtree[u]
    edge_loads: Dict[Tuple[int, int], float] = {}
    for u in G.nodes():
        if u in Mset:
            continue
        p = parent[u]
        edge_loads[_canonical_edge(u, p)] = subtree[u]
    rho = max(edge_loads.values()) if edge_loads else 0.0
    return RootedResult(rho=rho, floor=(1.0/rho if rho > 0 else float("inf")),
                        parent=parent, distance={u: qinv*depth[u] for u in G.nodes()},
                        edge_loads=edge_loads)


def best_of_randomized_forests(G: nx.Graph, obj: ChainObjects, marks: Iterable[int],
                               repeats: int = 8, seed: int = 0,
                               jitter: float = 0.15) -> RootedResult:
    """Sound target-aware refinement: choose the best rho among valid forests.

    Each trial perturbs edge lengths only to choose a different path system;
    rho is then recomputed with the original conductances.  Since every trial
    individually satisfies Theorem 5, taking the maximum floor (minimum rho)
    remains a valid lower floor.  This is a comparator/refinement, not a new theorem.
    """
    best = rooted_congestion(G, obj, marks)
    rng = np.random.default_rng(seed)
    edges = [_canonical_edge(*e) for e in G.edges()]
    for _ in range(repeats):
        # Log-normal factor is positive and close to one.
        factors = np.exp(rng.normal(0.0, jitter, size=len(edges)))
        perturb = {e: float(f) for e, f in zip(edges, factors)}
        trial = rooted_congestion(G, obj, marks, perturb=perturb)
        if trial.rho < best.rho:
            best = trial
    return best
