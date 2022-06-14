'''allocation.py
Helper functions for calculating the DFD values.


- Import functions from tree_cable_allocation
  - functionalize functions
  - re-implement with NetworkX
  - calculate Cumulative and Dead Ranges (out of product_fibre_ranges [24, 48, 72, 96, 144, 288, 432])
  - calculate Capacities based on Calculated Capacity from PPC Addresses -> Live Counts

- Additional Functions:
  - Total Civil Meters (Display in Green)
  - Total Hours spent designing FSA 
    - since start?
  - Designed by
  - Approved by
  - Phase PRE, CMR, DFD, OFC, OFX
  - File connected to:
'''

import pandas as pd
import numpy as np
import networkx as nx

# create DFs from Excel File
def load_file(file, node_sheet="Node", wire_sheet="Wire"):
    # TODO: add methods for loading from dot (graphviz), 
    # TODO: add method for loading the graph directly
    nodes_df = load_excel(file, "Node")
    edges_df = load_excel(file, "Wire")
    return nodes_df, edges_df

def load_excel(file, sheet="Node"):
    return pd.read_excel(file, sheet_name=sheet, header=0)

# create G from DF if needed
def create_graph(edges_df):
    start = edges_df.columns.to_list()[1]
    end = edges_df.columns.to_list()[2]
    G = nx.from_pandas_edgelist(edges_df, start, end, edge_attr=edges_df.columns.to_list(), edge_key=end)
    return G

def create_tree(G):
    return nx.dfs_tree(G)

def filter_max(cable_list):
    return max(filter(None, cable_list))

# preorder traversal for Cable Activities
# followed by postorder traversal for Structure Activities (SpliceNo)
def cable_activities(G, edges_df, act=302, capacity=432):  # nodes_df, edges_df,
    # Calculate Cable Activities and Store in List
    cable_list = []

    splices = list({k for k, v in nx.dfs_predecessors(
        G, source=0).items() if v == 0})
    splices.append(0)

    # CableActivity calculation
    for node in list(nx.dfs_preorder_nodes(G)):
        if node in splices:
            if node == 0:
                pass
            else:
                cable_list.append(None)

        else:
            # TODO: ERROR: this erroneously allocates the same Cable Activity to siblings. Only children can be the Cable Activities.
            # if is_child(node, prev_node) and (prev_capacity == capacity): 
            #       no increment
            # else:
            #       increment
            prev_capacity = capacity
            capacity = edges_df.at[edges_df.index[edges_df["End"]
                                                  == node][0], "Cap"]
            # Previous Activity Code if SSS
            if (capacity != prev_capacity):
                act += 1
            cable_list.append(act)

    print(cable_list)
    return True, cable_list

def splice_activities(G, nodes_df, cable_list, offset=0):
    act = filter_max(cable_list)+offset # Skip some number of ActivityCodes as a buffer
    # print("Start", act)
    splice_list = [None]*len(nodes_df)

    splices = list({k for k, v in nx.dfs_predecessors(
        G, source=0).items() if v == 0})
    splices.append(0)

    # SpliceNo (Structure Activity) calculation
    for node in list(nx.dfs_postorder_nodes(G)):
        # Catch null nodes
        if np.isnan(node):
            # print("Node:", node)
            pass
        # Catch splices
        if node in splices:
            if node == 0:
                # print("Node:", node, " is FDH, skipping splice activity allocation.")
                pass
            else:
                # print("Node:", node, "is splice, skipping splice activity allocation.")
                pass
        else:
            check_live = nodes_df.at[nodes_df.index[nodes_df["NODE"] == node][0], "Live"]
            # If Live is INT
            if not np.isnan(check_live):
                act += 1
                # print("Node: ", node, "Splice Activity: ", act)
                splice_list[nodes_df.index[nodes_df["NODE"]==node].tolist()[0]]=act

            # Skip if no HSDP (No Live)
            else:
                # print("Node:", node, "has no live fibres, skipping splice activity allocation.")
                splice_list[nodes_df.index[nodes_df["NODE"]==node].tolist()[0]]=None
    
    return True, splice_list

## USAGE:
# cable_activities(G, edges_df)
# splice_activities(G, nodes_df, cable_list)
# edges_df["CableActivity"] = activities(G)

def add_node_attributes(G, nodes_df):
    node_attrs = {}
    cols = nodes_df.columns
    for node in nodes_df["NODE"]:
        node_attrs[node] = {}
        for col in cols:
            # print(col, nodes_df.at[node, col])
            node_attrs[node][col] = nodes_df.at[node, col]    
    nx.set_node_attributes(G, node_attrs)

 
# def cumulative_ranges(G, nodes_df, edges_df):
#     for node in list(nx.dfs_postorder_nodes(G)):
#         thisNode = G.nodes[node]
#         s1, e1, = thisNode["HSDP_start"], thisNode["SPARE_end"]
#         print(node, s1, e1, (e1-s1+1))

#         n_slice = nodes_df[nodes_df["NODE"]==node]
#         e_slice = edges_df[edges_df["End"]==node]
#         print(n_slice["HSDP_start"], n_slice["SPARE_end"], e_slice["Cap"])
#         cable_sizes = [24, 48, 72, 96, 144, 288, 432]

#         # Formula for the cumulative range:
#         rowIndex = edges_df[edges_df["End"]==node]
#         edges_df.loc[rowIndex, "CumulativeRange"] = node.successors()

#         min_val = 24
#         for size in cable_sizes :
#             if min_val > size and size > k :
#                 min_val = size


# Calculate cumulative ranges at each node using the Tree structure
def cumulative_ranges(T):
    # Call add attributes if not existing
    s = "HSDP_start"
    e = "SPARE_end"

    # Add leaf nodes to list
    leaf_nodes = [node for node in T.nodes() if T.in_degree(node)!=0 and T.out_degree(node)==0]
    
    for node in nx.dfs_postorder_nodes:
        sum = 0
        sum += T.nodes[node][e] - T.nodes[node][s] + 1