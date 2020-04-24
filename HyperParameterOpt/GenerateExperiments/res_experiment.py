from rescomp import ResComp, specialize
import pickle
from scipy import sparse
import networkx as nx
from math import floor
from lorenz_sol import *

def how_long_accurate(u, pre, tol=1):
    """ Find the first i such that ||u_i - pre_i||_2 > tol """
    for i in range(u.shape[1]):
        dist = np.sum((u[:,i] - pre[:,i])**2)**.5
        if dist > tol:
            return i
    return u.shape[1]

def remove_edges(A,nedges):
    """ Randomly removes 'nedges' edges from a sparse matrix 'A'
    """
    A.todok()
    # Remove Edges
    keys = list(A.keys())
    remove_idx = np.random.choice(range(len(keys)),size=nedges, replace=False)
    remove = [keys[i] for i in remove_idx]
    for e in remove:
        A[e] = 0
    return A
    
def barab1():
    """ Barabasi-Albert preferential attachment. Each node is added with one edge
    """
    n = np.random.randint(2000,3500)
    m = 2
    A = nx.adj_matrix(nx.barabasi_albert_graph(n,m)).T
    return sparse.dok_matrix(A)
    
def barab2():
    """ Barabasi-Albert preferential attachment. Each node is added with two edges
    """
    n = np.random.randint(2000,3500)
    m = 2
    A = nx.adj_matrix(nx.barabasi_albert_graph(n,m)).T
    return sparse.dok_matrix(A)

def erdos():
    """ Erdos-Renyi random graph. p=2/n
    """
    n = np.random.randint(2000,3500)
    p = 2/n
    A = nx.adj_matrix(nx.erdos_renyi_graph(n,m)).T
    return sparse.dok_matrix(A)
    
def random_digraph():
    """ Random digraph. Each directed edge is present with probability p=2/n
    """
    n = np.random.randint(2000,3500)
    p = 2/n
    return sparse.random(n,n, density=p, data_rvs=np.ones, format='dok')

def watts():
    """ Watts-Strogatz small world model
    """
    n = np.random.randint(2000,3500)
    k = 5
    p = .05
    A = nx.adj_matrix(nx.watts_strogatz_graph(n,k,p)).T
    return sparse.dok_matrix(A)

def random_lorenz_x0():
    return  20*(2*np.random.rand(3) - 1)

def experiment(fname, network_adj, 
             res_params, diff_eq_params,
             ntrials=1000,  norbits=5, 
             x0=random_lorenz_x0, remove_p=0
            ):
    """ Tests the reservoir computers generated by the given hyper parameters 
        on 'norbits' different orbits
    """
    
    # Make dictionary to store data
    results = {i:{'net':None, 'pred':[], 'err':[]} for i in range(ntrials)}

    i = 0
    while i < ntrials:
        net = network_adj()
        # Remove Edges
        if remove_p != 0:
            net = remove_edges(net,floor(remove_p*np.sum(net != 0)))
        results[i]["net"] = net
        
        
        for j in range(norbits):

            # Initial condition
            diff_eq_params["x0"] = x0()
            train_t, test_t, u = rc_solve_ode(diff_eq_params)
            c = ResComp(net, **res_params)

            # Train network
            results[i]["err"].append(rc.fit(train_t, u))
            results[i]["pred"].append(how_long_accurate(u(test_t), rc.predict(test_t), tol=TOL))

        i += 1
        rc_save_results(fname, results)
        print(f"Net complete-- \nNet: {network_adj} \nPercent {remove_p}")
