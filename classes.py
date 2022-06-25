#############################################

#               NODES!                      #

#############################################
class Node:
    "This is a node"
    id = ""
    capacity = 12
    splices = 4
    spliceID = -1
    sheet = ""
    fcp = ""
    live = 0
    spare = 0
    activity = 300


#############################################

#               CABLES!                     #

#############################################


class Wire:
    "This is a class to define a Fibre Optic Cable"
    id = ""
    path = ""
    startNode = ""
    endNode = ""

class Cable(Wire):
    activity = 300
    capacity = 1
    cumulativeRange = (0,0)
    deadRange = (0,0)

    def edge_label(self):
        print(f'{self.activity}\n{self.capacity}\n{self.cumulativeRange}\nD, {self.deadRange}')

def TopologicalSort(G, nx.post_order_dfs):
    pass

# How can I implement a TopologicalSort that takes in a 
# graph and computes the list of nodes starting from a 
# particular start (int / string), and skipping the list for 
# elements not in the set
# Furthermore, we have types of data like SB-1142A3-1 where 
# 3 is {SpliceDir2} and could have been {SpliceDir1} instead
# We may even encounter more numbers of SpliceDir beyond 1 and 2, 
# so having it be a recursive implementation where we
# first sort along SpliceDir1, then SpliceDir2, etc for dirs in
# splicedir
# Mostly, we have a startNum, SetCondition (i.e. )