import networkx as nx
from random import random as random
from random import normalvariate as normal
from math import sqrt as sqrt

# for a set of nodes in a weighted, directed graph g, calculate
# the assortativity with respect to a specified property or pair
# of properties
def weighted_assortativity(g, nodes, property1, property2=None):

    if len(nodes)<2:  # if there are not enough nodes, return None
        return None

    if not property2:         # if only one property is specified
        property2 = property1 # use it at both ends of each edge

    # calculate the sum of the edge weights between all the specified nodes
    W = sum([ w["weight"] for i,j,w in g.edges(data=True) if i in nodes and j in nodes ])

    # list the weighted properties for source nodes, and then for target nodes in set the set of nodes
    weighted_x_values = [ w["weight"] * g.nodes[i][property1] for i,k,w in g.edges(data=True) if i in nodes and j in nodes ]
    weighted_y_values = [ w["weight"] * g.nodes[j][property2] for k,j,w in g.edges(data=True) if k in nodes and j in nodes ]

    # calculate xbar_sou and ybar_tar
    x_bar = sum(weighted_x_values)/W
    y_bar = sum(weighted_y_values)/W

    # calculate sigma_x and sigma_y
    x_sd = sqrt( sum([ w["weight"] * pow(g.nodes[i][property1] - x_bar, 2) for i,k,w in g.edges(data=True) if i in nodes and k in nodes]) /W)
    y_sd = sqrt( sum([ w["weight"] * pow(g.nodes[j][property2] - y_bar, 2) for k,j,w in g.edges(data=True) if k in nodes and j in nodes]) /W)

    # calculate the numerator: the sum the weighted differences between properties and average properties
    weighted_diffs = sum( [ w['weight'] * (g.nodes[i][property1] - x_bar) * (g.nodes[j][property2] - y_bar) for i,j,w in g.edges(data=True) if i in nodes and j in nodes ])

    if W * x_sd * y_sd > 0:  # if the denominator is positive
        return weighted_diffs / (W * x_sd * y_sd)  # the final assortativity value
    else:
        return None          # otherwise avoid division by zero by returning None

# some code to test the function with...
g = nx.complete_graph(100).to_directed()  # a complete directed network with 100 nodes

for i in g.nodes:
    g.nodes[i]['state'] = normal(0, 1)

for i, j in g.edges:
    g[i][j]['weight'] = random()

print(weighted_assortativity(g, g.nodes, "state"))