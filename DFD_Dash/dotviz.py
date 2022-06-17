from DFD_Dash.allocation import *
from DFD_Dash.upload import *

import pandas as pd
import pydot
import networkx as nx

from tkinter.filedialog import askdirectory, askopenfilename
import os, time, shutil

try:
    data_directory = askdirectory(title="Select Rhino Output directory:")
except ModuleNotFoundError as me:
    print(me)
except NameError as ne:
    print(ne) 
    data_directory = "/Data/1142A/" # "/Users/patrickwilkie/Documents/Work/KadTec/DFD/Fiber Layout/1142A"

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
    nodes_dff = nodes_df.loc[:0] # Add FDH # TODO: Slice only FDH? This assumes the FDH and SV1 are the first two entries.

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

    # TODO: remove duplicates

    return nodes_df

nodes_df = sort_nodes(nodes_df, edges_df)

## Save the pandas objects as csv
nodes_df.to_csv(data_directory+"/nodes.csv", index=None)
edges_df.to_csv(data_directory+"/edges.csv", index=None)

## Create NetworkX object from dictionaries
# G = create_graph(edges_df)
G = nx.from_pandas_edgelist(edges_df, edges_df.columns.tolist()[0], edges_df.columns.tolist()[1], edge_attr=edges_df.columns.to_list(), edge_key=edges_df.columns.tolist()[1])

## For attribute in dictionaries, add to NetworkX Graph
nodes_dff = nodes_df # Choose a subset of the Attributes to Add [['Splice', 'Sheet', 'Struc', 'LiveCount', 'SpareCount', 'ServingAreaCount']]
print(len(nodes_dff))
nodes_dff = nodes_dff.drop_duplicates(subset=['Struc'])
print(len(nodes_dff))

node_attr = nodes_dff.set_index('Struc').to_dict('index')
nx.set_node_attributes(G, node_attr)

# Check an edge for attributes!
G.edges[('SB-1142A3-4', 'SB-1142A3-5')]

## Create PyDot Visualization Using the Edge Style from Templates


## Use HTML Templates for each Structure Type
GD = pydot.Dot('test_graph', 
            graph_type='graph', 
            layout="dot",
            concentrate="true",
            rankdir="LR",
            orderoutput="edgesfirst",
            splines="compound", 
            nodesep="1", 
            ranksep="1")

graph = nx.drawing.nx_pydot.to_pydot(G)
graph.write_png('out.png')
graph.write_pdf('out.pdf')
GD.to_string()

graphs = pydot.graph_from_dot_data(dot_string)


ddx = nx.to_dict_of_dicts(G)
importer = DictImporter()
ddxA = importer.import_(ddx)
print(RenderTree(ddxA))
print(nx.draw(G))

A = nx.nx_agraph.to_agraph(G)

import matplotlib.pyplot as plt
import pydot
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()

pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
nx.draw(G, pos=pos)
plt.show()

graphs = pydot.graph_from_dot_file('graphviz/fsa_1031B.dot')
graph = graphs[0]

graph.write_png('output.png')
graph.write_pdf("output.pdf")
graph.create_svg()

G = nx.drawing.nx_pydot.from_pydot(graph)

# Generate Graph Outputs
OUTPATH = "Data/1142A/"
if not os.path.exists(OUTPATH):
    os.mkdir(OUTPATH)
else:
    pass

# Pickle a Graph
nx.write_gpickle(G, OUTPATH+'out.pkl')

# JSON a Graph
nx.tree_data

nx.cytoscape_data(G, attrs=)

# node_attr_list = list(set(np.array([list(G.nodes[n].keys()) for n in G.nodes()]).flatten()))
node_attr_list = list(set([k for n in G.nodes for k in G.nodes[n].keys()]))
for i in range(0, len(node_attr_list)):
    nx.get_node_attributes(G, node_attr_list[i])