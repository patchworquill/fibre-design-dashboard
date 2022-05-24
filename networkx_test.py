import networkx
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import tinydb

from tkinter.filedialog import askdirectory, askopenfilename

file=askopenfilename(title="Select Fibre Data Excel File (Array Format with sheets named 'Node' and 'Wire'")


# TODO: remove hardcoded File
file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\(Fibre Data) OKRG 1031B.xlsx'

####################################################
## 
##                  PART 1
## 
##      Collate XY into Fibre Data from Rhino
##          
##
####################################################

# READ EDGE DATA IN
edges = pd.read_excel(file, sheet_name="Wire", header=0)
G = networkx.from_pandas_edgelist(edges, "Start", "End", edge_attr=["Cap", "CableActivity"], edge_key="End")

networkx.draw_kamada_kawai(G)  # networkx draw()
networkx.draw_spring(G)
networkx.draw_spectral(G)
networkx.draw_random(G)
networkx.draw_circular(G)
plt.show()

nodes = pd.read_excel(file, sheet_name="Node", header=0)

# READ SHEET NAMES FROM RHINO EXPORT]
path = os.path.split(file)[0]
sheet_names = path+"/R/Rhino_Tree_Node_Export.csv"
df_sheets = pd.read_csv(sheet_names, header=None)
df_sheets.columns = ["Sheet Number","Structure", "X", "Y"]

result = pd.merge(nodes, df_sheets, how='left', left_on=['Struc'], right_on=['Structure'], validate="one_to_many") # one_to_one
result = result.drop(["Structure"], axis=1)

## This data structure (dictionary of dictionaries), enables us to search the FSA by Structure ID
node_lbl={result["NODE"][idx]:{key: result[key][idx] for idk, key in enumerate(result.columns)} for idx, i in enumerate(result["Struc"])}

# x, y = list(result["X"], result["Y"])
keys = node_lbl.keys()
values = { key : (node_lbl[key]['X'], node_lbl[key]["Y"]) for key in node_lbl.keys()}
# TODO: remove hardcoded FDH point setting
# values['FDH'] = values['SV-1031B1-1']
# values['SV-1031B1-2'] = values['SV-1031B1-1']

values['FDH'] = values[1]
values[2] = values[1]


edge_lbl=G.edges.data()
type(G.nodes.data())

# posx = networkx.nx_pydot.graphviz_layout(G, prog='not', root=0) 
posx = values
networkx.draw_networkx(G, pos=posx, width=1, linewidths=1, node_size=500, node_color='pink', alpha=0.9, labels=node_labels)
networkx.draw_networkx_edge_labels(G, pos=posx, edge_labels={(1,3): "First", (20, 21): "Another One"}, font_color='red')
plt.show()
    # TODO: Use nodelist and edgelist to remove PB nodes from the view
plt.savefig('gv_neato.png')
plt.savefig('gv_neato.pdf')

cy = networkx.readwrite.json_graph.cytoscape_data(G)

node_keys = ["NODE", 'Struc', 'SpliceNo', 'SheetNo', 'FCP', 'Type', 'SSS', 'Live', 'SPARE']
slice_node_label = result[node_keys]
names = []
for node in list(slice_node_label.index):
    this_str = '\n'.join(str(x) for x in slice_node_label.values.tolist()[node])
    this_str = this_str.replace("nan", '')
    names.append(this_str)

try:    
    node_labels = {node: names[node] for node in node_lbl.keys()}
    node_lbl[0] = node_lbl['FDH']
    print('Renamed Node FDH to Node 0.') 
    node_lbl.pop('FDH')
except KeyError:
    print("No node called 'FDH'")

opath = path+"\Py"