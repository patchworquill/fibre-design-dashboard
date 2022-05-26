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
    nodes_df = pd.read_excel(file, sheet_name=node_sheet, header=0)
    edges_df = pd.read_excel(file, sheet_name=wire_sheet, header=0)
    return nodes_df, edges_df

# create G from DF if needed


def create_graph(edge_list):
    G = nx.from_pandas_edgelist(edge_list, "Start", "End", edge_attr=[
        "Cap", "CableActivity"], edge_key="End")
    return G

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
                # print("FDH")
                pass
            else:
                # print("Skipping splice node:", node)
                cable_list.append(None)

        else:
            prev_capacity = capacity
            capacity = edges_df.at[edges_df.index[edges_df["End"]
                                                  == node][0], "Cap"]
            # Previous Activity Code if SSS
            if (capacity != prev_capacity):
                act += 1
            cable_list.append(act)
            # print(node.name, "Cable Activity: ", act)
    # print("Finished Calculating Cable Activity")

    return True, cable_list

def filter_max(cable_list):
    return max(filter(None, cable_list))

def splice_activities(G, nodes_df, cable_list, offset=0):
    act = filter_max(cable_list)+offset # Skip some number of ActivityCodes as a buffer
    print("Start", act)
    splice_list = [None]*len(nodes_df)

    splices = list({k for k, v in nx.dfs_predecessors(
        G, source=0).items() if v == 0})
    splices.append(0)

    # SpliceNo (Structure Activity) calculation
    for node in list(nx.dfs_postorder_nodes(G)):
        # Catch null nodes
        if np.isnan(node):
            print("Node:", node)
        # Catch splices
        if node in splices:
            if node == 0:
                print("FDH, skipping splice activity allocation.")
            else:
                print("Skipping splice at node:", node)
                # splice_list.insert(None, node)
        else:
            check_live = nodes_df.at[nodes_df.index[nodes_df["NODE"] == node][0], "Live"]
            # If Live is INT
            if not np.isnan(check_live):
                act += 1
                splice_list[node]=act
                # print("Node: ", node, "Splice Activity: ", act)

            # Skip if no HSDP (No Live)
            else:
                print("Node: ", node, "has no live fibres, skipping splice activity allocation.")
                # check_rsvd = nodes_df.at[nodes_df.index[nodes_df["NODE"] == node][0], "RSVD"].sum() + nodes_df.at[nodes_df.index[nodes_df["NODE"] == node][0], "RSVD2"]
                # else:
                
                    # splice_list.insert(None, node)
    
    # sort according to node order
    return True, splice_list


## USAGE:
# cable_activities(G, edges_df)
# splice_activities(G, nodes_df, cable_list)
# edges_df["CableActivity"] = activities(G)