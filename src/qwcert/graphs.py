from __future__ import annotations
from typing import Dict, Iterable, List, Tuple
import math
import numpy as np
import networkx as nx


def _relabel(G: nx.Graph) -> nx.Graph:
    return nx.convert_node_labels_to_integers(G, ordering="sorted")


def make_graph(family: str, requested_n: int, seed: int = 0) -> Tuple[nx.Graph, Dict[str, int]]:
    """Generate benchmark graphs using the declared experiment configuration."""
    n = int(requested_n)
    if family == "path":
        G = nx.path_graph(n)
    elif family == "cycle":
        G = nx.cycle_graph(n)
    elif family == "grid":
        side = max(2, int(round(math.sqrt(n))))
        G = nx.grid_2d_graph(side, side)
        G = _relabel(G)
    elif family == "barbell":
        # Two dense lobes connected by a path; total is exactly 2*m1+m2.
        m1 = max(3, n // 4)
        m2 = max(1, n - 2*m1)
        G = nx.barbell_graph(m1, m2)
    elif family == "lollipop":
        m = max(3, n // 2)
        path_n = max(1, n - m)
        G = nx.lollipop_graph(m, path_n)
    elif family == "random_regular":
        if n % 2 == 1:
            n += 1
        # deterministic retry sequence until connected
        for j in range(100):
            G = nx.random_regular_graph(3, n, seed=seed*1009+j)
            if nx.is_connected(G):
                break
        else:
            raise RuntimeError("failed to sample connected random regular graph")
    elif family == "block_model":
        if n < 8:
            n = 8
        n1 = n // 2
        sizes = [n1, n-n1]
        p_in = min(0.35, max(6.0/n, 0.08))
        p_out = min(0.05, max(1.5/n, 0.005))
        probs = [[p_in, p_out], [p_out, p_in]]
        for j in range(200):
            G = nx.stochastic_block_model(sizes, probs, seed=seed*1009+j)
            G = nx.Graph(G)
            if nx.is_connected(G):
                break
        else:
            raise RuntimeError("failed to sample connected SBM")
    else:
        raise ValueError(f"unknown family {family}")
    G = _relabel(nx.Graph(G))
    return G, {"requested_n": requested_n, "realized_n": G.number_of_nodes(), "seed": seed}


def choose_mark(G: nx.Graph, policy: str, graph_seed: int = 0, policy_index: int = 0) -> int:
    nodes = sorted(G.nodes())
    if policy == "first":
        return nodes[0]
    if policy == "last":
        return nodes[-1]
    deg = dict(G.degree())
    if policy == "highest_degree":
        mx = max(deg.values())
        return min(u for u in nodes if deg[u] == mx)
    if policy == "lowest_degree":
        mn = min(deg.values())
        return min(u for u in nodes if deg[u] == mn)
    if policy == "seeded_random":
        rng = np.random.default_rng(1_000_003 + 10_007*graph_seed + 97*policy_index + G.number_of_nodes())
        return int(rng.choice(nodes))
    raise ValueError(policy)


def cubic_block_chain(core: nx.Graph, edge: Tuple[int,int], L: int) -> Tuple[nx.Graph, int, int]:
    """Replace one core edge by the cubic block chain from Theorem 3.

    Returns (G, easy_target, hard_target).  L>=2 is assumed.
    """
    if L < 2:
        raise ValueError("L must be >=2")
    core = nx.convert_node_labels_to_integers(core, ordering="sorted")
    u, v = edge
    if not core.has_edge(u, v):
        raise ValueError("edge absent")
    G = core.copy()
    G.remove_edge(u, v)
    if not nx.is_connected(G):
        raise ValueError("selected edge is a bridge")
    next_id = G.number_of_nodes()
    blocks: List[List[int]] = []
    # B_1,...,B_{L-1}: K4 minus disjoint edges (0,1),(2,3).
    for _ in range(L-1):
        vs = list(range(next_id, next_id+4)); next_id += 4
        B = nx.complete_graph(vs)
        B.remove_edge(vs[0], vs[1]); B.remove_edge(vs[2], vs[3])
        G.add_nodes_from(B.nodes()); G.add_edges_from(B.edges())
        blocks.append(vs)
    # B_L terminal: K4 minus one edge (0,1), whose endpoints are ports.
    vs = list(range(next_id, next_id+4)); next_id += 4
    B = nx.complete_graph(vs); B.remove_edge(vs[0], vs[1])
    G.add_nodes_from(B.nodes()); G.add_edges_from(B.edges())
    blocks.append(vs)
    # Attach u,v to first block's first port pair.
    G.add_edge(u, blocks[0][0]); G.add_edge(v, blocks[0][1])
    # Each nonterminal block uses ports [2,3] to next block [0,1].
    for j in range(L-1):
        G.add_edge(blocks[j][2], blocks[j+1][0])
        G.add_edge(blocks[j][3], blocks[j+1][1])
    if any(d != 3 for _, d in G.degree()):
        raise RuntimeError("cubic construction failed degree check")
    easy = min(core.nodes())
    hard = blocks[-1][2]  # degree-3 terminal vertex, not an interface port
    return G, easy, hard


def _effective_resistance_edge(G: nx.Graph, edge: Tuple[int,int]) -> float:
    """Effective resistance for one edge via grounded sparse Laplacian solve."""
    u, v = edge
    nodes = sorted(G.nodes())
    idx = {x:i for i,x in enumerate(nodes)}
    L = nx.laplacian_matrix(G, nodelist=nodes).astype(float).tocsr()
    # ground last node; solve L_g x=b_g
    ground = len(nodes)-1
    keep = np.arange(len(nodes)-1)
    Lg = L[keep][:, keep].tocsc()
    b = np.zeros(len(nodes))
    b[idx[u]] += 1.0; b[idx[v]] -= 1.0
    bg = b[:-1]
    xg = np.asarray(__import__('scipy').sparse.linalg.spsolve(Lg, bg))
    x = np.zeros(len(nodes)); x[:-1]=xg
    return float(b @ x)


def select_low_resistance_edge(core: nx.Graph, seed: int = 0, samples: int = 24) -> Tuple[Tuple[int,int], float]:
    """Sample non-bridge edges and choose the smallest measured resistance."""
    bridges = {tuple(sorted(e)) for e in nx.bridges(core)}
    candidates = [tuple(sorted(e)) for e in core.edges() if tuple(sorted(e)) not in bridges]
    if not candidates:
        raise RuntimeError("no nonbridge edge")
    rng = np.random.default_rng(seed)
    if len(candidates) > samples:
        ids = rng.choice(len(candidates), size=samples, replace=False)
        candidates = [candidates[int(i)] for i in ids]
    scored = [(e, _effective_resistance_edge(core, e)) for e in candidates]
    return min(scored, key=lambda z: z[1])


def make_cubic_instance(core_m: int, seed: int = 0) -> Tuple[nx.Graph, int, int, Dict[str,float]]:
    if core_m % 2:
        raise ValueError("3-regular graph needs even m")
    for j in range(200):
        core = nx.random_regular_graph(3, core_m, seed=seed*1009+j)
        if nx.is_connected(core):
            break
    else:
        raise RuntimeError("failed connected cubic core")
    core = nx.convert_node_labels_to_integers(core, ordering="sorted")
    e, re = select_low_resistance_edge(core, seed=seed)
    L = int(math.floor(math.sqrt(core_m)))
    G, a, z = cubic_block_chain(core, e, L)
    # easy target should be a core vertex away from deleted edge if possible
    candidates = [x for x in core.nodes() if x not in e]
    a = min(candidates) if candidates else 0
    return G, a, z, {"core_m": core_m, "L": L, "N": G.number_of_nodes(), "edge_u": e[0], "edge_v": e[1], "edge_resistance": re}
