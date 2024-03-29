import sys
import os
import time
import networkx as nx 
import pickle
import community as community_louvain

from random import random as random
from random import normalvariate as normal
from random import uniform as uniform
from random import shuffle as shuffle
from random import seed as seed
from csv import writer

sweeper = [] # list of all possible paramter combinations
II = 5 #  number of runs per combination
vals = [0.01,0.03,0.1,0.3] # possible values we sweep over 
T  = 1000       # number of time steps
Dt = 0.1        # size of each time step
n = 30        # number of opinion states
epsilon  = 0.1  # scale of random drift

# create a list of dictionaries, where each element of the list contains a parameter combination
for c in vals:
    for h in vals:
        for a in vals:
            for theta_h in vals:
                for theta_a in vals:
                    sweeper.append({'c':c, 'h':h, 'a':a, 'theta_h':theta_h, 'theta_a':theta_a})

# gets parameter values and builds the network for each combination in sweeper in the range start to end 
def get_para_values(start, end):
    for loc in range(start, end+1):
        c = sweeper[loc]['c'] # get the parameter values to build the corresponding network 
        h = sweeper[loc]['h']
        a = sweeper[loc]['a']
        theta_h = sweeper[loc]['theta_h']
        theta_a = sweeper[loc]['theta_a']
        build(c, h, a, theta_h, theta_a) # calls a function to build the network

# builds the network and dumps in a pickle file
def build(c, h, a, theta_h, theta_a):
    for ii in range(1):
        filename = f"output/{c}-{h}-{a}-{theta_h}-{theta_a}-{ii}.pkl"

        if os.path.exists(filename): 
            continue # if we've already built and saved network ii then skip over it
        else:
            start_time = time.time()
            print("Running", filename, "... ", end='')
            initialize(c, h, a, theta_h, theta_a)
            t = T / 100
            for tt in range(T): # complete T steps, each lasting time Dt
                if tt % t == 0:
                    print(tt, end=' ')
                update()
            print('')
            end_time = time.time()
            print("elapsed time: {:.2f}".format(end_time - start_time))
            get_statistics(g)
            #store_statistics(ii, c, h, a, theta_h, theta_a, avg_edgw, com, mod_com, range_avg_com, sd_avg_com)
            #pickle.dump(g, open(filename, 'wb'))



# get statistics of a network
def get_statistics(dir_graph):

    # gets average edge weight of undirected graph (sum of all edge weights / total number of edge weights)
    sum_edgw = 0
    num_edgw = 0
    edge_list = [dir_graph[i][j]['weight'] for i, j in dir_graph.edges()] # list of edge weights
    for edge in edge_list: 
        sum_edgw += edge 
        num_edgw += 1 
    avg_edgw = sum_edgw / num_edgw # average edge weight
    print("SUM OF EDGE WEIGHTS ", sum_edgw)
    print("NUM OF EDGE WEIGHTS ", num_edgw)
    print("AVERAGE EDGE WEIGHT IS ", avg_edgw)
    h = convert(dir_graph) # converts the directed network to an undirected network for community analysis
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
    var_avgcommstate = (1/len(avgcommstates)) * sum([((avgcommstate - avg_avgcommstate) ** 2) for avgcommstate in avgcommstates])
    std_avgcommstate = var_avgcommstate ** 0.5
    print(avg_edgw, num_comms, mod, range_avgcomm, std_avgcommstate)

# convert directed network to undirected network
def convert(dir):
    # converts directed graph to undirected graph 
    # by averaging weight of two directed edges between a pair of nodes into one undirected weight
    h = nx.complete_graph(n) # undirected version of directed graph => same no. of nodes
    for i in h.nodes:
        h.nodes[i]['state'] = dir.nodes[i]['state'] # each node i has the same opinion as directed graph
        h.nodes[i]['c'] = dir.nodes[i]['c'] # each node i has the same parameter value as directed graph
        h.nodes[i]['h'] = dir.nodes[i]['h']
        h.nodes[i]['a'] = dir.nodes[i]['a']
        h.nodes[i]['theta_h'] = dir.nodes[i]['theta_h']
        h.nodes[i]['theta_a'] = dir.nodes[i]['theta_a']
    for i, j in h.edges:
        itoj = dir[i][j]['weight']
        jtoi = dir[j][i]['weight']
        avg = (itoj+jtoi) / 2
        h[i][j]['weight'] = avg 
    return h

# initialise the network with random opinions and connections
def initialize(c, h, a, theta_h, theta_a): # add h_strat and a_strat
    global g

    g = nx.complete_graph(n).to_directed() # create directed graph with 100 nodes

    for i in g.nodes:
        g.nodes[i]['state'] = normal(0, 1) # each node's opinion

        # give each node two "updaters": h_update and a_update
        # each of which can be a string like "max", "min", "avg"
        # if h_strat=="rnd": g.nodes[i]['h_update] == choice(["max", "min", "avg"])
        # if a_strat=="rnd": g.nodes[i]['a_update] == choice(["max", "min", "avg"])
        # minmin, minmax, maxmin, maxmax, avgavg, rndrnd
        g.nodes[i]['c'] = c 
        g.nodes[i]['h'] = h
        g.nodes[i]['a'] = a 
        g.nodes[i]['theta_h'] = theta_h
        g.nodes[i]['theta_a'] = theta_a

    for i, j in g.edges:
        g[i][j]['weight'] = random() # random weight value in range [0,1]
    
    opinions = [g.nodes[i]['state'] for i in g.nodes]
    opinions.sort(reverse=True)
    weights = [g[i][j]['weight'] for i, j in g.edges]
    weights.sort(reverse=True)
    #print("THE OPINIONS ARE ", opinions)
    #print("THE WEIGHTS ARE ", weights)

# updates opinions and connections
def update():
    global g

    nodes = list(g.nodes)
    shuffle(nodes)

    for i in nodes:
        nbs = list(g.neighbors(i))

        total = sum(g[i][j]['weight'] for j in nbs) # the total incoming weights to node i

        if total > 0:
            # conformity
            # iterate over the D dimensions applying conformity to each one

            av = sum(g[i][j]['weight'] * g.nodes[j]['state'] for j in nbs) / total
            g.nodes[i]['state'] += g.nodes[i]['c'] * (av - g.nodes[i]['state']) * Dt

            afterconf = [g.nodes[i]['state'] for i in g.nodes]
            afterconf.sort(reverse=True)
            #print("AFTER CONFORMITY STATES ARE", afterconf)

            # neophily
            for j in nbs:
                diff = abs(av - g.nodes[j]['state'])
                #max_diff = min([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
                g[i][j]['weight'] += g.nodes[i]['a'] * (diff - g.nodes[i]['theta_a']) * Dt
            
            afterneo = [g[i][j]['weight'] for i, j in g.edges]
            afterneo.sort(reverse=True)
            # print("AFTER NEOPHILY WEIGHTS ARE ", afterneo)

        # homophily
        for j in nbs:
            # diff = [abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)]
            # if g.nodes[i]["h_update"] == "max": diff = max(diff)
            # if g.nodes[i]["h_update"] == "min": diff = min(diff)
            # if g.nodes[i]["h_update"] == "avg": diff = sum(diff)/D
            diff = abs(g.nodes[i]['state'] - g.nodes[j]['state'])
            #max_diff = max([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
            #min_diff = min([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])
            #mean_diff = sum([abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)])/D

            # diff is going to be a function of two vectors?
            g[i][j]['weight'] += g.nodes[i]['h'] * (g.nodes[i]['theta_h'] - diff) * Dt

            if g[i][j]['weight'] < 0:
                g[i][j]['weight'] = 0

        afterhomo = [g[i][j]['weight'] for i, j in g.edges]
        afterhomo.sort(reverse=True)
        #print("AFTER HOMOPHILY WEIGHTS ARE ", afterhomo)
        # random drift
        g.nodes[i]['state'] += normal(0, epsilon)
        afterdrift = [g.nodes[i]['state'] for i in g.nodes]
        afterdrift.sort(reverse=True)
        #print("AFTER DRIFT IS ", afterdrift)

def main():
    build(0.01, 0.3, 0.01, 0.01, 0.1)

main()

# SET N = 25 
# RUN 1 DIM CASE WITHOUT NEOPHILY ON BOTH AND COMPARE (SEE IF PROBLEM IN NEOPHILY PART OF CODE)