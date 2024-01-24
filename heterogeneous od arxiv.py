# A version of Sayama's (2020) model where each agent may have
# their own parameter values for c, h, a, theta_h and theta_a

import networkx as nx 
import matplotlib.pyplot as plt

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
distribution = "normal"  # or "uniform"
c_range = [0.25, 0.025]  # interpreted as [mean,std dev] when distribution is "normal", otherwise [min,max] of a uniform distribution
h_range = [0.05, 0.025]
a_range = [0.25, 0.025]
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

        g.nodes[i]['c'] = get_param(c_range, distribution=distribution)
        g.nodes[i]['h'] = get_param(h_range, distribution=distribution)
        g.nodes[i]['a'] = get_param(a_range, distribution=distribution)
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
            #max_diff = max([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
            #min_diff = min([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
            #mean_diff = sum([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])/D

            # diff is going to be a function of two vectors?
            g[i][j]['weight'] += g.nodes[i]['h'] * (g.nodes[i]['theta_h'] - diff) * Dt

            if g[i][j]['weight'] < 0:
                g[i][j]['weight'] = 0

        # random drift
        g.nodes[i]['state'] += normal(0, epsilon)

homophoity_avgs = []
neophlic_avgs = []
conformity_avgs = []
reps = [i for i in range(1,II)]
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
        #pos = nx.spring_layout(g)
        #nx.draw_networkx_nodes(g, pos)
        #nx.draw_networkx_labels(g, pos)
        #nx.draw_networkx_edges(g, pos)
        #plt.show()
        # pickle the final network and dump it to disk
        pickle.dump(g, open(filename, 'wb'))
