from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import math
import numpy as np
import networkx as nx
from scipy import sparse
from scipy.sparse import linalg as spla


@dataclass
class ChainObjects:
    nodes: List[int]
    node_to_idx: Dict[int, int]
    P: sparse.csr_matrix
    pi: np.ndarray
    D: sparse.csr_matrix
    degrees: np.ndarray
    m_edges: int


def lazy_random_walk_objects(G: nx.Graph) -> ChainObjects:
    """One-half-lazy simple random walk and reversible discriminant.

    P(x,x)=1/2 and P(x,y)=1/(2 d_x) on undirected edges.
    pi_x=d_x/(2|E|).  Node order is sorted for deterministic artifacts.
    """
    if not nx.is_connected(G):
        raise ValueError("G must be connected")
    nodes = sorted(G.nodes())
    node_to_idx = {u: i for i, u in enumerate(nodes)}
    n = len(nodes)
    m = G.number_of_edges()
    deg = np.array([G.degree(u) for u in nodes], dtype=float)
    if np.any(deg <= 0):
        raise ValueError("isolated node")
    rows: List[int] = []
    cols: List[int] = []
    vals: List[float] = []
    for i, u in enumerate(nodes):
        rows.append(i); cols.append(i); vals.append(0.5)
        w = 0.5 / deg[i]
        for v in G.neighbors(u):
            rows.append(i); cols.append(node_to_idx[v]); vals.append(w)
    P = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    pi = deg / (2.0 * m)
    sqrt_pi = np.sqrt(pi)
    inv_sqrt_pi = 1.0 / sqrt_pi
    D = sparse.diags(sqrt_pi) @ P @ sparse.diags(inv_sqrt_pi)
    D = ((D + D.T) * 0.5).tocsr()  # numerical symmetrization
    return ChainObjects(nodes, node_to_idx, P, pi, D, deg, m)


def mark_indices(obj: ChainObjects, marks: Iterable[int]) -> Tuple[np.ndarray, np.ndarray]:
    mark_set = {obj.node_to_idx[u] for u in marks}
    M = np.array(sorted(mark_set), dtype=int)
    if len(M) == 0 or len(M) == len(obj.nodes):
        raise ValueError("marked set must be nonempty and proper")
    U = np.array([i for i in range(len(obj.nodes)) if i not in mark_set], dtype=int)
    return M, U


def dirichlet_objects(obj: ChainObjects, marks: Iterable[int]):
    M, U = mark_indices(obj, marks)
    Duu = obj.D[U][:, U].tocsr()
    K = sparse.eye(len(U), format="csr") - Duu
    Z = float(obj.pi[U].sum())
    b = np.sqrt(obj.pi[U] / Z)
    Puu = obj.P[U][:, U].tocsr()
    A = sparse.eye(len(U), format="csr") - Puu
    return M, U, K, b, Z, A


def smallest_eigenvalue_spd(K: sparse.csr_matrix) -> float:
    n = K.shape[0]
    if n <= 4:
        return float(np.linalg.eigvalsh(K.toarray())[0])
    try:
        # Shift-invert targets the smallest eigenvalue efficiently for sparse SPD K.
        val = spla.eigsh(K, k=1, sigma=0.0, which="LM", return_eigenvectors=False, tol=1e-10, maxiter=max(2000, 10*n))[0]
        return float(val)
    except Exception:
        try:
            val = spla.eigsh(K, k=1, which="SA", return_eigenvectors=False, tol=1e-9, maxiter=max(3000, 12*n))[0]
            return float(val)
        except Exception:
            return float(np.linalg.eigvalsh(K.toarray())[0])


def global_spectral_gap(obj: ChainObjects) -> float:
    n = len(obj.nodes)
    if n <= 5:
        eig = np.linalg.eigvalsh(obj.D.toarray())
        eig.sort()
        return float(1.0 - eig[-2])
    try:
        eig = spla.eigsh(obj.D, k=2, which="LA", return_eigenvectors=False, tol=1e-10, maxiter=max(5000, 20*n))
        eig = np.sort(eig)
        return float(max(0.0, 1.0 - eig[-2]))
    except Exception:
        eig = np.linalg.eigvalsh(obj.D.toarray())
        eig.sort()
        return float(max(0.0, 1.0 - eig[-2]))


def reference_hitting_time(obj: ChainObjects, marks: Iterable[int]) -> Tuple[float, float]:
    """Stationary-conditioned hitting time and relative linear residual."""
    M, U, K, b, Z, A = dirichlet_objects(obj, marks)
    x = spla.spsolve(K.tocsc(), b)
    H = float(b @ x)
    rel = float(np.linalg.norm(K @ x - b) / max(np.linalg.norm(b), 1e-300))
    return H, rel


@dataclass
class CGCertificate:
    lower: float
    upper: float
    width: float
    iterations: int
    converged: bool
    residual_norm: float
    x: np.ndarray


def cg_certificate(K: sparse.csr_matrix, b: np.ndarray, ell: float,
                   rel_width_tol: float = 0.05, maxiter: int = 200) -> CGCertificate:
    """Exact-arithmetic-inspired CG interval evaluated in floating point.

    The proposal recurrence is ordinary CG from zero.  At each iteration the
    diagnostic interval is L=b^T x and U=L+||r||^2/ell.  This is the numerical
    benchmark analogue; formal post-validation is performed separately.
    """
    if ell <= 0:
        raise ValueError("ell must be positive")
    x = np.zeros_like(b)
    r = b.copy()
    p = r.copy()
    rr = float(r @ r)
    if rr == 0:
        return CGCertificate(0.0, 0.0, 0.0, 0, True, 0.0, x)
    lower = 0.0
    upper = rr / ell
    converged = False
    it = 0
    for k in range(1, maxiter + 1):
        Ap = K @ p
        denom = float(p @ Ap)
        if denom <= 0:
            break
        alpha = rr / denom
        x = x + alpha * p
        r = r - alpha * Ap
        rr_new = float(r @ r)
        lower = float(b @ x)
        upper = float(lower + rr_new / ell)
        width = float((upper - lower) / max(lower, 1e-30))
        it = k
        if width <= rel_width_tol:
            converged = True
            rr = rr_new
            break
        if rr_new <= 1e-30:
            converged = True
            rr = rr_new
            break
        beta = rr_new / rr
        p = r + beta * p
        rr = rr_new
    width = float((upper - lower) / max(lower, 1e-30))
    return CGCertificate(lower, upper, width, it, converged, math.sqrt(max(rr, 0.0)), x)


def proposal_h_from_kx(x: np.ndarray, pi_u: np.ndarray, Z: float) -> np.ndarray:
    """Map K-coordinate proposal x to a proposal y for A h=1."""
    return np.sqrt(Z / pi_u) * x
