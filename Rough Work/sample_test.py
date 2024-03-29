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
n = 100   # number of opinion states
epsilon  = 0.1  # scale of random drift
D = 1 # number of dimensions 

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

# builds the network and dumps in a pickle file -> skip pickle dump and 5 runs
def build(c, h, a, theta_h, theta_a):        
        
        for ii in range(1):
            #filename = f"output/{c}-{h}-{a}-{theta_h}-{theta_a}-{ii}.pkl"
            #if os.path.exists(filename): 
            #    continue # if we've already built and saved network ii then skip over it
            #else:
            start_time = time.time()
        #print("Running", filename, "... ", end='')
            initialize(c, h, a, theta_h, theta_a, "min", "max")
            t = T / 100
            for tt in range(T): # complete T steps, each lasting time Dt
                if tt % t == 0:
                    print("CURRENT TIME STEP IS ", tt )
                    #print(tt, end=' ')
                    update()
            #print('')
            end_time = time.time()
            print("elapsed time: {:.2f}".format(end_time - start_time))
            get_statistics(g)
            #store_statistics(ii, c, h, a, theta_h, theta_a, avg_edgw, com, mod_com, range_avg_com, sd_avg_com)
                #pickle.dump(g, open(filename, 'wb'))

def store_statistics(ii, c, h, a, theta_h, theta_a, avg_edgw, com, mod_com, range_avg_com, sd_avg_com):
    with open('max_min.csv', 'a') as stats:
        writer_object = writer(stats)
        writer_object.writerow([ii, c, h, a, theta_h, theta_a, avg_edgw, com, mod_com, range_avg_com, sd_avg_com])
    stats.close()

# get statistics of a network -> added try except block because of error 
def get_statistics(dir_graph):

    # gets average edge weight of undirected graph (sum of all edge weights / total number of edge weights)
    sum_edgw = 0
    num_edgw = 0
    edge_list = [dir_graph[i][j]['weight'] for i, j in dir_graph.edges()] # list of edge weights
    # print("EDGE LIST IS " , edge_list)
    for edge in edge_list: 
        sum_edgw += edge 
        num_edgw += 1 
    print("THE SUM OF THE EDGE WEIGHTS IS ", sum_edgw)
    print("THE NUMBER OF EDGE WEIGHTS IS ", num_edgw)
    avg_edgw = sum_edgw / num_edgw # average edge weight
    print("AVERAGE EDGE WEIGHT IS ", avg_edgw)
    
    h = convert(dir_graph) # converts the directed network to an undirected network for community analysis
    try:
        nodescomms =community_louvain.best_partition(h)
        comms = list(dict.fromkeys(list(nodescomms.values()))) # gets only the community
        num_comms = len(comms) # get the number of communities
        print("NUM COMMS IS ", num_comms)
        nodesgrouped = {} 
        for key, value in nodescomms.items():
            nodesgrouped.setdefault(value, []).append(key) # groups the nodes together with respect to their communities
        nodesgroupedlist = list(nodesgrouped.values()) # turns this grouping into a list
        mod = nx.community.modularity(h, nodesgroupedlist) # gets the modularity of communities 
        print("MOD IS ", mod)
        range_avgcomms = [] # range in each dimension
        stds_avgcomms = [] # standard deviation in each dimension
        for d in range(D):
            avgcommstates = [] # average state of each community
            for comm in nodesgroupedlist: 
                sumstates = 0
                numstates = 0
                for i in comm:
                    sumstates += h.nodes[i]['state'][d]
                    numstates += 1
                avgcommstates.append(sumstates/numstates)
            range_avgcomms.append(max(avgcommstates) - min(avgcommstates))

            avg_avgcommstate = sum(avgcommstates) / len(avgcommstates) # finds average of all community's average state 
            var_avgcommstate = (1/len(avgcommstates)) * sum([((avgcommstate - avg_avgcommstate) ** 2) for avgcommstate in avgcommstates])
            std_avgcommstate = var_avgcommstate ** 0.5 # standard deviation in each dimension
            stds_avgcomms.append(std_avgcommstate)

        range_avgcomm = sum(range_avgcomms) / len(range_avgcomms)
        std_avgcommstate = sum(stds_avgcomms) / len(stds_avgcomms)

        #return avg_edgw, num_comms, mod, range_avgcomm, std_avgcommstate
    
    except:
        #min_edge = min(edge_list)
        #max_edge = max(edge_list)
        #for i, j in h.edges:
        #    h[i][j]['weight'] = (h[i][j]['weight'] - min_edge) / (max_edge - min_edge)
        nodescomms =community_louvain.best_partition(h)
        comms = list(dict.fromkeys(list(nodescomms.values())))
        num_comms = len(comms) # get the number of communities
        print("NUM COMMS IS IN EXCEPTIONAL CASE ", num_comms)
        nodesgrouped = {} 
        for key, value in nodescomms.items():
            nodesgrouped.setdefault(value, []).append(key) # groups the nodes together with respect to their communities
        nodesgroupedlist = list(nodesgrouped.values()) # turns this grouping into a list
        mod = nx.community.modularity(h, nodesgroupedlist) # gets the modularity of communities 
        print("MOD IS IN EXTREME CASE ", mod)
        # print("Final edge list is " , edge_list)
        #return avg_edgw,-1,-1,-1,-1
    

# convert directed network to undirected network
def convert(dir):
    # converts directed graph to undirected graph 
    # by averaging weight of two directed edges between a pair of nodes into one undirected weight
    h = nx.complete_graph(n) # undirected version of directed graph => same no. of nodes
    for i in h.nodes:
        h.nodes[i]['state'] = dir.nodes[i]['state']
        # h.nodes[i]['state'] = dir.nodes[i]['state'] # each node i has the same opinion as directed graph -> maybe issue with multi dim cas
        h.nodes[i]['c'] = dir.nodes[i]['c'] # each node i has the same parameter value as directed graph
        h.nodes[i]['h'] = dir.nodes[i]['h']
        h.nodes[i]['a'] = dir.nodes[i]['a']
        h.nodes[i]['theta_h'] = dir.nodes[i]['theta_h']
        h.nodes[i]['theta_a'] = dir.nodes[i]['theta_a']
        h.nodes[i]["h_update"] = dir.nodes[i]["h_update"]
        h.nodes[i]["a_update"] = dir.nodes[i]["a_update"]
    for i, j in h.edges:
        itoj = dir[i][j]['weight']
        jtoi = dir[j][i]['weight']
        avg = (itoj+jtoi) / 2
        h[i][j]['weight'] = avg 
    return h

# initialise the network with random opinions and connections -> states initialisation changed 
def initialize(c, h, a, theta_h, theta_a, poss_h, poss_a): # add h_strat and a_strat
    global g
    #print("C IS" , c)
    #print("A IS ", a)
    #print("H IS ", h)
    #print("THETA_H IS " , theta_h)
    #print("THETA_A IS " , theta_a)
    g = nx.complete_graph(n).to_directed() # create directed graph with 100 nodes

    for i in g.nodes:
        g.nodes[i]['state'] = [0] * D # each node's opinion
        for d in range(D):
            g.nodes[i]['state'][d] += normal(0,1) # each node's opinion
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
        g.nodes[i]['h_update'] = poss_h
        g.nodes[i]["a_update"] = poss_a

    for i, j in g.edges:
        g[i][j]['weight'] = random() # random weight value in range [0,1]
    
    opinions = [g.nodes[i]['state'] for i in g.nodes]
    weights = [g[i][j]['weight'] for i, j in g.edges]
    weights = []
    print("OPINIONS ARE AT INITIALISATION ", opinions)
    print("WEIGHTS ARE AT INITIALISATION ", weights)

def update_loops():
    nodes = list(g.nodes)
    shuffle(nodes)
    for i in nodes:

        nbs = list(g.neighbors(i))

         # list of edge weights
       

        total = sum(g[i][j]['weight'] for j in nbs) # the total incoming weights to node i
        if total > 0:
            # conformity
            # iterate over the D dimensions applying conformity to each one
            for d in range(D):
                av = sum(g[i][j]['weight'] * g.nodes[j]['state'][d] for j in nbs) / total
                g.nodes[i]['state'][d] += g.nodes[i]['c'] * (av - g.nodes[i]['state'][d]) * Dt
            # print("OPINION OF NODE I IS NOW ", g.nodes[i]['state'])    
            # neophily
            for j in nbs:
                diffs = []
                for d in range(D):
                    av = (sum(g[i][j]['weight'] * g.nodes[j]['state'][d] for j in nbs) / total)
                    diffs.append(abs(av - g.nodes[j]['state'][d])) 
                if g.nodes[i]["a_update"] == "max":
                    diff = max(diffs)
                elif g.nodes[i]["a_update"] == "min":
                    diff = min(diffs)
                else:
                    diff = sum(diffs) / D 
                
                #print("DIFF IS FOR NEOPHILY", diffs)
                #print("theta_a is", theta_a)
                
                g[i][j]['weight'] += g.nodes[i]['a'] * (diff - g.nodes[i]['theta_a']) * Dt

        # homophily
        for j in nbs:
            diff = [abs(g.nodes[i]['state'][d] - g.nodes[j]['state'][d]) for d in range(D)]
            #print("DIFF IS FOR HOMOPHILY ", diff)
            #print("theta_h is", theta_h)
            if g.nodes[i]["h_update"] == "max": 
                diff = max(diff)
            elif g.nodes[i]["h_update"] == "min":
                diff = min(diff)
            else:
                diff = sum(diff) / D 
            
            g[i][j]['weight'] += g.nodes[i]['h'] * (g.nodes[i]['theta_h'] - diff) * Dt
            

            if g[i][j]['weight'] < 0:
                g[i][j]['weight'] = 0
        # random drift
        for d in range(D):
            g.nodes[i]['state'][d] += normal(0, epsilon)
    
# updates opinions and connections
def update():
    global g
    weights = [g[i][j]['weight'] for i, j in g.edges]
    print("THE WEIGHTS ARE ", weights)

    opinions = [g.nodes[i]['state'] for i in g.nodes]
    print("OPINIONS ARE ", opinions)
   
    update_loops()
    
    weights = [g[i][j]['weight'] for i, j in g.edges]
    print("AFTER UPDATE WEIGHTS ARE ", weights)

    opinions = [g.nodes[i]['state'] for i in g.nodes]
    print("AFTER UPDATE OPINIONS ARE ", opinions)

def main():
    #args = sys.argv[1:] # gets command line arguments in a list
    #slice = args[0]
    # need to check the arguments for validity (do later)
    #start = (int(slice) - 1) * 32 # 320 
    # end = start + 31
    build(0.01, 0.3, 0.01, 0.01, 0.1)

main()