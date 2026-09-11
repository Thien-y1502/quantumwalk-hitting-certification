import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import networkx as nx
import numpy as np
from scipy.sparse import linalg as spla
from qwcert.core import lazy_random_walk_objects, dirichlet_objects, reference_hitting_time, proposal_h_from_kx
from qwcert.rooted import rooted_congestion
from qwcert.rational import rooted_rho_fraction_half_lazy, exact_validate_half_lazy_graph


def test_exact_certificate_contains_reference():
    G=nx.path_graph(12); mark=0; obj=lazy_random_walk_objects(G); M,U,K,b,Z,A=dirichlet_objects(obj,[mark])
    x=spla.spsolve(K.tocsc(),b); h=proposal_h_from_kx(np.asarray(x),obj.pi[U],Z)
    root=rooted_congestion(G,obj,[mark]); rho=rooted_rho_fraction_half_lazy(G,mark,root.parent)
    cert=exact_validate_half_lazy_graph(G,mark,h,rho); H,_=reference_hitting_time(obj,[mark])
    assert float(cert['lower']) <= H <= float(cert['upper'])*(1+1e-12)
