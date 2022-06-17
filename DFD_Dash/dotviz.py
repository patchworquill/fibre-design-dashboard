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
        print(sb)
        this = splices.loc[splice_indices[i]].tolist()
        index = edges_df[edges_df['Start SB']==sb]['Number'].tolist()[0]
        print("Start SB index:", index)
        index -= 0.5 # Insert BEFORE index matching Start SB
        edges_df.loc[index] = this
        print("INDEX:", index, "\nITEM:", this)

    edges_df = edges_df.sort_index().reset_index(drop=True)
    return edges_df

sort_edges(edges_df)

## Add FDH -> SV to EDGES
# fdhEdges = edges_df[edges_df['Parent Path']=="FDH"]
# splices = fdhEdges['Start SB'].unique().tolist()

# for splice in splices:
#     print("Adding splice", splice, "to Cable List")
#     row = pd.DataFrame([["FDH", splice]], columns = ['Start SB', 'End SB'])
#     edges_df = pd.concat([row, edges_df])

def add_splices(edges_df):
    fdhEdges = edges_df[edges_df['Parent Path']=="FDH"]
    splices = fdhEdges['Start SB'].unique().tolist()
    
    for splice in splices:
        print("Adding splice", splice, "to Cable List")
        row = pd.DataFrame([["FDH", splice]], columns = ['Start SB', 'End SB'])
        edges_df = pd.concat([row, edges_df])

    return edges_df

def reindex(df):
    cableID = []
    for idx, data in enumerate(df[df.columns[0]]):
        cableID.append(idx)

    df['Index'] = cableID
    df.set_index('Index')
    return df

edges_df = add_splices(edges_df)
edges_df = reindex(edges_df)
edges_df = edges_df.set_index('Index')



# edges_df.drop('Number') # Remove 'Number' column, which has been replaced by 'index'

# Reindex
# cableID = []
# for idx, endSB in enumerate(edges_df[edges_df.columns[0]]):
#     cableID.append(idx)

# edges_df['Number'] = cableID
# edges_df.set_index('Number')



# Sort Edges

# Move SV to 

## Add FDH -> SV to NODES

# Sort nodes_df according to order of appearance in edges_df








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