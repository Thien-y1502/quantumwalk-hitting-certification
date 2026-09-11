import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import networkx as nx
import numpy as np
from qwcert.core import lazy_random_walk_objects, global_spectral_gap, reference_hitting_time, dirichlet_objects, smallest_eigenvalue_spd
from qwcert.rooted import rooted_congestion


def test_path_calibration():
    # Use an 11-state path for a direct soundness check.
    n=10; G=nx.path_graph(n+1); obj=lazy_random_walk_objects(G); root=rooted_congestion(G,obj,[0])
    # This test checks certificate soundness for the standard half-lazy graph walk.
    H,_=reference_hitting_time(obj,[0])
    assert root.rho + 1e-9 >= H


def test_rooted_floor_below_dirichlet():
    G=nx.barbell_graph(4,3); obj=lazy_random_walk_objects(G); root=rooted_congestion(G,obj,[0])
    _,_,K,_,_,_=dirichlet_objects(obj,[0]); lam=smallest_eigenvalue_spd(K)
    assert root.floor <= lam*(1+1e-8)


def test_reference_positive():
    G=nx.cycle_graph(12); obj=lazy_random_walk_objects(G); H,r=reference_hitting_time(obj,[0])
    assert H>0 and r<1e-9
