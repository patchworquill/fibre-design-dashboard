from DFD_Dash.allocation import *
from DFD_Dash.upload import *

import pandas as pd
import pydot
import networkx as nx

from tkinter.filedialog import askdirectory, askopenfilename
import os, time, shutil

try:
    data_directory = askdirectory(title="Select Rhino Output directory:")
except NameError, ModuleNotFoundError as e:
    print(e)
    data_directory = "/Users/patrickwilkie/Documents/Work/KadTec/DFD/Fiber Layout/1142A"

os.path.exists(data_directory)
dir_list = os.listdir(data_directory)
for file in dir_list:
    if "Node" in file:
        node_file = data_directory + "/" + file
    elif "Cable" in file:
        edge_file = data_directory + "/" + file

nodes_df = pd.read_csv(node_file)
edges_df = pd.read_csv(edge_file)

def sort_edges(edges_df):
    splices = edges_df[edges_df['Parent Path']=="FDH"]
    splice_ends = splices['End SB'].tolist()
    splice_indices = splices.index.tolist()
    edges_df = edges_df.drop(splice_indices, axis=0)
    
    for i, sb in enumerate(splice_ends):
        print("Sorting", sb)
        this = splices.loc[splice_indices[i]].tolist()
        index = edges_df[edges_df['Start SB']==sb]['Number'].tolist()[0]
        print("Start SB index:", index)
        index -= 0.5 # Insert BEFORE index matching Start SB
        edges_df.loc[index] = this
        print("INDEX:", index, "\nITEM:", this)

    edges_df = edges_df.sort_index().reset_index(drop=True)
    edges_df['Number'] = edges_df.index
    return edges_df

edges_df = sort_edges(edges_df)

def add_splices(edges_df):
    fdhEdges = edges_df[edges_df['Parent Path']=="FDH"]
    splices = fdhEdges['Start SB'].unique().tolist()
    
    for splice in splices:
        print("Adding splice", splice, "to Cable List")
        row = pd.DataFrame([["FDH", splice]], columns = ['Start SB', 'End SB'])
        edges_df = pd.concat([row, edges_df])
    edges_df = edges_df.sort_index().reset_index(drop=True)
    edges_df['Number'] = edges_df.index

    return edges_df

edges_df = add_splices(edges_df)

# Sort nodes_df according to order of appearance in edges_df
# First appearance of node adds it to list! Use append.
def sort_nodes(nodes_df, edges_df):
    nodes_dff = nodes_df.loc[0:1] # Add FDH

    for i, node in  enumerate(edges_df['End SB'].tolist()):
        if node in nodes_dff['Struc'].tolist():
            print(node, 'already in sorted DataFrame.')
            pass
        else:
            # print(node)
            this = nodes_df[nodes_df['Struc']==node]
            nodes_dff = pd.concat([nodes_dff, this])

    nodes_df = nodes_dff.reset_index(drop=True)
    nodes_df['Splice'] = nodes_df.index

    return nodes_df

nodes_df = sort_nodes(nodes_df, edges_df)

## Save the pandas objects as csv
nodes_df.to_csv(data_directory+"/nodes.csv", index=None)
edges_df.to_csv(data_directory+"/edges.csv", index=None)

## Create Graphviz object from dictionaries

## For attribute in dictionaries, add

## Use HTML Templates for each Structure Type



G = create_graph(edges_df)

ddx = nx.to_dict_of_dicts(G)
importer = DictImporter()
ddxA = importer.import_(ddx)
print(RenderTree(ddxA))
print(nx.draw(G))

A = nx.nx_agraph.to_agraph(G)

import matplotlib.pyplot as plt
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
import pydot
nx.nx_pydot.graphviz_layout(G, prog='dot')

graphs = pydot.graph_from_dot_file('graphviz/fsa_1031B.dot')
graph = graphs[0]

graph.write_png('output.png')
graph.write_pdf("output.pdf")
graph.create_svg()

G = nx.drawing.nx_pydot.from_pydot(graph)