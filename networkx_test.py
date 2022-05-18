import networkx
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

from tkinter.filedialog import askdirectory, askopenfilename
file=askopenfilename()

####################################################
## 
##                  PART 1
## 
##      Collate XY into Fibre Data from Rhino
##          
##
####################################################

# READ MAIN DATA IN
nodes = pd.read_excel(file, sheet_name="Node", header=0)
edges = pd.read_excel(file, sheet_name="Wire", header=0)

G = networkx.from_pandas_edgelist(edges, "Start", "End", edge_attr=["Cap", "CableActivity"], edge_key="End")

networkx.draw(G)  # networkx draw()
plt.savefig('foo.png')
plt.savefig('foo.pdf')

networkx.draw_spring(G)
plt.savefig('foo.png')
plt.savefig('foo.pdf')

networkx.draw_circular(G)
plt.show()

# READ SHEET NAMES FROM RHINO EXPORT]
path = os.path.split(file)[0]
sheet_names = path+"/R/Rhino_Tree_Node_Export.csv"
df_sheets = pd.read_csv(sheet_names, header=None)
df_sheets.columns = ["Sheet Number","Structure", "X", "Y"]

result = pd.merge(nodes, df_sheets, how='left', left_on=['Struc'], right_on=['Structure'], validate="one_to_many") # one_to_one

node_labels={"Struc "+str(idx):i for idx, i in enumerate(result["Struc"])}
x, y = result["X"], result["Y"]
pos = {} 
networkx.draw_networkx(G, pos=, arrows=True, labels=node_labels)