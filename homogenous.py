
# a homogenous version of the model where each node has the same fixed c, h and a 

import networkx as nx 
import matplotlib.pyplot as plt
import community as community_louvain

from random import random as random
from random import normalvariate as normal
from random import uniform as uniform
from random import shuffle as shuffle
from random import seed as seed

import time

import os
import pickle

# seed pseudo-random number generator
seed()

# Main Parameters

n  = 100       # number of network nodes
T  = 1000       # number of time steps
Dt = 0.1        # size of each time step
II = 10         # number of replicates to run
epsilon  = 0.1  # scale of random drift

# We can either specify a normal distribution for each parameter or a uniform distribution for each parameter
# if the limits of the uniform distribution are equal then the values will be identical (homogeneous)
distribution = "uniform"  # or "normal"
c_range = [(0.01+0.3)/2, (0.01+0.3)/2]  # for the homogenous case, each node has a fixed c, h and a 
h_range = [(0.01+0.3)/2, (0.01+0.3)/2]
a_range = [(0.01+0.3)/2, (0.01+0.3)/2]
theta_h_range = [0.03, 0.03]  # this fixes the theta_h values at 0.03
theta_a_range = [0.03, 0.03]  # this fixes the theta_a values at 0.03


# generate a uniform random floating point value in the specified range
# or a normally distributed random floating point value with specified mean and std dev
def get_param(dist_params, distribution="uniform"):

    a, b = dist_params

    if "normal" in distribution:
        val = normal(a,b)
        return min(0.3, max(val,0.0)) # clip the value to lie in the range [0.0,0.3] (not sure)

    return uniform(a,b)


# initialise a directed graph with no self connections, normally distributed internal state and random weights
def initialize():
    global g

    g = nx.complete_graph(n).to_directed() # create directed graph with 100 nodes

    for i in g.nodes:
        g.nodes[i]['state'] = normal(0, 1) # each node's opinion

        g.nodes[i]['c'] = get_param(c_range, distribution="fixed")
        g.nodes[i]['h'] = get_param(h_range, distribution="fixed")
        g.nodes[i]['a'] = get_param(a_range, distribution="fixed")
        g.nodes[i]['theta_h'] = get_param(theta_h_range, distribution="fixed")
        g.nodes[i]['theta_a'] = get_param(theta_a_range, distribution="fixed")

    for i, j in g.edges:
        g[i][j]['weight'] = random() # random weight value in range [0,1] 

    g.pos = nx.spring_layout(g, weight='weight', k=0.3) # read into this further


# update the weights and internal state of every node in a network
# according to 1) social conformity, 2) homophily, 3) neophily, 4) random drift
def update():
    global g

    nodes = list(g.nodes)
    shuffle(nodes)

    for i in nodes:
        nbs = list(g.neighbors(i))

        total = sum(g[i][j]['weight'] for j in nbs) # the total incoming weights to node i

        if total > 0:
            # conformity
            av = sum(g[i][j]['weight'] * g.nodes[j]['state'] for j in nbs) / total
            g.nodes[i]['state'] += g.nodes[i]['c'] * (av - g.nodes[i]['state']) * Dt

            # neophily
            for j in nbs:
                diff = abs(av - g.nodes[j]['state'])
                #max_diff = min([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
                g[i][j]['weight'] += g.nodes[i]['a'] * (diff - g.nodes[i]['theta_a']) * Dt

        # homophily
        for j in nbs:
            diff = abs(g.nodes[i]['state'] - g.nodes[j]['state'])
            g[i][j]['weight'] += g.nodes[i]['h'] * (g.nodes[i]['theta_h'] - diff) * Dt

            if g[i][j]['weight'] < 0:
                g[i][j]['weight'] = 0

        # random drift
        g.nodes[i]['state'] += normal(0, epsilon)

def get_parameter_values(h):

    # gets average edge weight (sum of all edge weights / total number of edge weights)
    sum_edgw = 0
    num_edgw = 0
    edge_list = [h[i][j]['weight'] for i, j in h.edges()] # list of edge weights
    for edge in edge_list: 
        sum_edgw += edge 
        num_edgw += 1 
    avg_edgw = sum_edgw / num_edgw # average edge weight

    nodescomms = community_louvain.best_partition(h) # gets the node and its community using the Louvain modularity maximisation method 
    comms = list(dict.fromkeys(list(nodescomms.values()))) # gets only the community
    num_comms = len(comms) # get the number of communities
    nodesgrouped = {} 
    for key, value in nodescomms.items():
        nodesgrouped.setdefault(value, []).append(key) # groups the nodes together with respect to their communities
    nodesgroupedlist = list(nodesgrouped.values()) # turns this grouping into a list
    mod = nx.community.modularity(h, nodesgroupedlist) # gets the modularity of communities 

    # finds the average community state  
    avgcommstates = [] # average state of each community 
    for comm in nodesgroupedlist:
        sumstates = 0
        numstates = 0
        for i in comm:
            sumstates += h.nodes[i]['state']
            numstates += 1 
        avgcommstates.append(sumstates/numstates)
    range_avgcomm = max(avgcommstates) - min(avgcommstates)

    # find standard deviation of average community states 
    avg_avgcommstate = sum(avgcommstates) / len(avgcommstates) # finds average of all community's average state 
    std_avgcommstate = sum([((comm - avg_avgcommstate) ** 2) for comm in avgcommstates]) / len(avgcommstates) ** 0.5 
    return avg_edgw, num_comms, mod, range_avgcomm, std_avgcommstate

def convert(g):
    # converts directed graph to undirected graph 
    # by averaging weight of two directed edges between a pair of nodes into one undirected weight
    h = nx.complete_graph(n) # undirected version of directed graph => same no. of nodes
    for i in h.nodes:
        h.nodes[i]['state'] = g.nodes[i]['state'] # each node i has the same opinion as directed graph
        h.nodes[i]['c'] = g.nodes[i]['c'] # each node i has the same parameter value as directed graph
        h.nodes[i]['h'] = g.nodes[i]['h']
        h.nodes[i]['a'] = g.nodes[i]['a']
        h.nodes[i]['theta_h'] = g.nodes[i]['theta_h']
        g.nodes[i]['theta_a'] = g.nodes[i]['theta_a']
    for i, j in h.edges:
        itoj = g[i][j]['weight']
        jtoi = g[j][i]['weight']
        if itoj > 0 and jtoi > 0: # if pair of nodes have two edges, then average the weights 
            avg = (itoj+jtoi) / 2
            h[i][j]['weight'] = avg 
        else:
            h[i][j]['weight'] = max(itoj, jtoi) # otherwise take the edge with weight not equal to 0
    return h

# loop over II independent replicates of the same network construction process
for ii in range(1):
    # construct an appropriate filename; we assume that the directory "output" exists
    filename = f"output/{n}-{T}-{Dt}-{distribution}-{c_range[0]}-{c_range[1]}-{h_range[0]}-{h_range[1]}-{a_range[0]}-{a_range[1]}-{theta_h_range[0]}-{theta_h_range[1]}-{theta_a_range[0]}-{theta_a_range[1]}-{ii}.pkl"

    if os.path.exists(filename):
        continue # if we've already built and saved network ii then skip over it
    else:
        start_time = time.time()
        print("Running", filename, "... ", end='')
        initialize()
        t = T / 100
        for tt in range(T): # complete T steps, each lasting time Dt
            if tt % t == 0:
                print(tt, end=' ')
            update()
        print('')
        end_time = time.time()
        print("elapsed time: {:.2f}".format(end_time - start_time))
        g_undirected = convert(g)
        avg_edge_weight, com, mod_com, range_com, sd_com = get_parameter_values(g_undirected)
        print(avg_edge_weight, com, mod_com, range_com, sd_com)
        # pickle the final network and dump it to disk
        pickle.dump(g_undirected, open(filename, 'wb'))

        network_pickle = open (filename, "rb")
        network = pickle.load(network_pickle)
        avg_edge_weight, com, mod_com, range_com, sd_com = get_parameter_values(network)
        print(avg_edge_weight, com, mod_com, range_com, sd_com)




