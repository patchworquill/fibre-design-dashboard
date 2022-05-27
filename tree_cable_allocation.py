# -*- coding: utf-8 -*-
"""tree-cable-allocation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pLsrrG9lWyXAvLy8Xz7Rop4p1YypGllY
"""

import pandas as pd
import numpy as np
import os
from ete3 import Tree

from tkinter.filedialog import askdirectory, askopenfilename
file=askopenfilename()

####################################################
## 
##                  PART 1
## 
##      Collate Sheet Numbers from Rhino
##          
##
####################################################

# READ MAIN DATA IN
df = pd.read_excel(file, sheet_name="Node", header=0)
dfc = pd.read_excel(file, sheet_name="Wire", header=0)

# READ SHEET NAMES FROM RHINO EXPORT]
path = os.path.split(file)[0]
sheet_names = path+"/R/Rhino_Tree_Node_Export.csv"
df_sheets = pd.read_csv(sheet_names, header=None)
df_sheets.columns = ["Sheet Number","Structure"]

result = pd.merge(df, df_sheets, how='left', left_on=['Struc'], right_on=['Structure'], validate="one_to_one") # one_to_one
result["SheetNo"] = result["Sheet Number"]
result = result.drop(["Sheet Number", "Structure"], axis=1)
if not os.path.exists(path+"/Py/"):
  os.mkdir(path+"/Py/")

result.to_excel(path+"/Py/(Fibre Data) OUT1.xlsx", index=None)
df = result

####################################################
## 
##                  PART 2
## 
##      Calculate the Cable Activity Numbers
##          
##
####################################################

t2 = Tree.from_parent_child_table(zip(dfc['Start'], dfc["End"]))
t2.describe()
# with open(path+"/Py/tree_description.txt", "w+") as f:
#   f.write(t2.describe())


fdhs = dfc.index[dfc["Start"]=="FDH"]
dfc_no_fdh = dfc.drop(fdhs)
capacity = 432 # Initialize to 432
act = 302

"""Let's get the `preorder` traversal of the tree. Later we will use this to compute:
- Cable Activity
"""
node_list = []
cable_list = []

for node in t2.traverse("preorder"):
    ## Skip if FDH (first node)
    
    if node.name =="FDH":
      print("FDH, skipping cable activity allocation.")
    ## Skip if Parent is FDH
    else:
      node_list.append(node.name)
      if node.up.name == "FDH":
        print("Parent is FDH")
        cable_list.append(None)
      else:
        prev_capacity = capacity
        capacity = dfc.at[dfc.index[dfc["End"]==node.name][0], "Cap"] 
        ## Skip if SSS
        if (capacity != prev_capacity):
          act += 1
        cable_list.append(act)
        print(node.name, "Cable Activity: ", act)

cac=pd.DataFrame(list(zip(node_list, cable_list)), columns=["list_End", "list_CableActivity"])
result = pd.merge(dfc, cac, left_on="End", right_on="list_End", validate="one_to_one")
result.to_excel(path+"/Py/(Fibre Data) OUT2.xlsx", index=None)

####################################################
## 
##                  PART 3
## 
##      Calculate the Splice Activity Numbers
##          
##
####################################################

node_list = []
splice_list = []

for node in t2.traverse("postorder"):
    ## Skip if FDH (first node)
    if node.name =="FDH":
      print("FDH, skipping splice activity allocation.")
    ## Skip if Parent is FDH
    else:
      node_list.append(node.name)
      if node.up.name == "FDH":
        print("Parent is FDH, skipping splice activity allocation.")
        splice_list.append(None)
      else:
        check_live = df.at[df.index[df["NODE"]==node.name][0], "Live"] 
        ## Skip if no HSDP (No Live)
        if not np.isnan(check_live):
          act += 1
          splice_list.append(act)
          print(node.name, "Splice Activity: ", act)
        else:
          print("No live fibres, skipping splice activity allocation.")
          splice_list.append(np.nan)

sac=pd.DataFrame(list(zip(node_list, splice_list)), columns=["list_End", "list_SpliceActivity"])
result = pd.merge(df, sac, left_on="NODE", right_on="list_End", validate="one_to_one")
result["SpliceNo"] = result["list_SpliceActivity"]
result = result.drop(result.columns[-2:], axis=1)
result.to_excel(path+"/Py/(Fibre Data) OUT3.xlsx", index=None)
df = result

####################################################
## 
##                  PART 4
## 
##            Calculate the FCP#
##          
##
####################################################

fcp_init = 21957

node_list = []
fcp_list = []
fcp = fcp_init

for node in t2.traverse("preorder"):
    ## Skip if FDH (first node)
    node_list.append(node.name)
    if (node.name or node.up.name) =="FDH":
      print("FDH or SV, skipping cable activity allocation.")
      fcp_list.append(None)
    ## Skip if Parent is FDH
    else:
      fcp += 1
      fcp_list.append(fcp)
      print(node.name, "FCP#", fcp)

l=pd.DataFrame(list(zip(node_list, fcp_list)), columns=["list_End", "FCP"])
# result = pd.merge(df, l, left_on="NODE", right_on="list_End", validate="one_to_one")
# result = result.drop(result.columns[-2:], axis=1)
df["FCP"] = fcp_list
result.to_excel(path+"/Py/(Fibre Data) OUT4.xlsx", index=None)

print("Final allocated FCP#:",fcp)

df = result

####################################################
## 
##                  PART 5
## 
##            Calculate the HSDP, SPARE
##          
##
####################################################

df["SPARE"] = np.ones(len(df))*12 - df["Live"]
for i in df["SPARE"]: 
  if i<0:
    df["SPARE"][i] = abs(df["SPARE"][i] / 12)*24

df["SPARE2"] = np.ones(len(df))*12 - df["RSVD"]
for i in range(0, len(df["SPARE2"])): 
  if i<0:
    df["SPARE2"][i] = abs(df["SPARE2"][i] / 12)*24

df["SPARE3"] = np.ones(len(df))*12 - df["RSVD2"]
for i in range(0, len(df["SPARE3"])):
  if i<0:
    df["SPARE3"][i] = abs(df["SPARE3"][i] / 12)*24

####################################################
## 
##                  PART 6
## 
##           Calculate the Allocated, Dead
##           This part replaces the Fiber Design 
##           Excel Process
##
####################################################

HSDP_start = []
HSDP_end, SPARE_start, SPARE_end = [], [], []
postorder = []

for node in t2.traverse("postorder"):
  postorder.append(node.name)
  print(node.name)

res = pd.merge(pd.DataFrame(zip(list(postorder))), df[["NODE", "Live", "SPARE", "RSVD", "SPARE2", "RSVD2", "SPARE3"]], left_on=0, right_on="NODE")
res = res[["NODE", "Live", "SPARE", "RSVD", "SPARE2", "RSVD2", "SPARE3"]]
res[["NODE", "Live", "SPARE", "RSVD", "SPARE2", "RSVD2", "SPARE3"]].to_clipboard(index=None, header=False)

## TODO: for now, we only care about the ranges, so we merge the RSVD into the LIVE counts?

## Calculate all the ranges
for idx, x in enumerate(res["NODE"]):
  ## For the first one, we start from 1 and initialize fresh lists
  ## TODO: do this with dataframes instead of lists
  if idx == 0:
    HSDP_start = [1]
    HSDP_end, SPARE_start, SPARE_end = [], [], []
  else:
    HSDP_start.append(SPARE_end[idx-1]+1)
  print(idx, x, HSDP_start[idx])
  HSDP_end.append(HSDP_start[idx] + res.at[idx, "Live"] - 1) ## TODO: Merge / Add all the LIVE / RSVD columns together?
  SPARE_start.append(HSDP_end[idx] + 1)
  SPARE_end.append(SPARE_start[idx] + res.at[idx, "SPARE"] - 1)

ranges = pd.DataFrame(zip([HSDP_start, HSDP_end, SPARE_start, SPARE_end]))

for idx, x in enumerate(res["Live"]):
  if np.isnan(x):
    print(idx, x)
    if not np.isnan(res.at[idx, "RSVD"]):
      # Add if not nan
      res.at[idx, "Live"] = res.at[idx, "RSVD"]
    if not np.isnan(res.at[idx, "RSVD2"]):
      res.at[idx, "Live"] += res.at[idx, "RSVD2"]
    if not np.isnan(res.at[idx, "Live"]):
      res.at[idx, "Spare"] = round(res.at[idx, "Live"]/12)*12 - res.at[idx, "Live"]
    else:
      pass


# After running this cell, I copy and pasted this into a blank text file
# Then, I renamed the file to .csv, and imported that into a sheet in excel
# Then, I copied the column to the NODE(T) sheet of the "flattened" fibre layout

"""Write out the Newick Tree of the FSA"""

t2.write(format=8) #features=["struc"],

"""## Pasting into AutoCAD

Below, change `n` to the value of the SB in question. If it is a PB, SV, or otherwise, change the text string below.
"""

n = 23 # change this to the number of the SB in question
struc = "SB-2061A3-"+str(n)
df[df['Struc']==struc]

this = df[df['Struc']=="SB-2061A3-"+inum]
this.iloc[0]["FCP"]

"""Example showing how to verify that the Fibre field is a string, and not a float, which it would be if it does not exist, since `NaN` is data type `float`"""

this = df.iloc[1]["Fibre"]
isinstance(this, str)

def string_constructor(struc):
  this = df[df['Struc']==struc]
  
  txt = "#"+str(this.iloc[0]["FCP"]).split("#")[1]
  txt += "\nFCP\n"
  txt += "F??? @"+struc+"\n"
  
  fsa = this.iloc[0]['Struc'].split("-")[1][:-1]
  txt += fsa +", "

  fibre = this.iloc[0]["Fibre"]
  spare = this.iloc[0]["Spare"]
  res = this.iloc[0]["Reserve"]

  # Append Fibre Range to String
  ## Start of Fibre Range
  if not isinstance(fibre, str):
    # print("Structure", struc, "has no HSDP fibre allocation.")
    txt += spare.split(",")[1].split("-")[0]
  else:
    txt += fibre.split(",")[1].split("-")[0]

  txt += "-"

  ## End of Fibre Range
  if not isinstance(spare, str):
    txt += fibre.split(",")[1].split("-")[1]
  else:
    txt += spare.split(",")[1].split("-")[1]

  ## TODO: Add RSVE counts case
  return txt


for struc in df.loc[:]["Struc"]:
  # n = 23
  # struc = "SB-2061A3-"+str(n)
  comment = string_constructor(struc)
  print(comment)
  with open(str(struc)+".txt", "w") as file:
      file.write(comment)
      file.close

# create a directory for the text files
try:
  !mkdir /text
except:
  print("directory /text/ must already exist")

# move all files into it
!mv *.txt text

!zip -r "text.zip" '/content/text'

from google.colab import files
files.download('text.zip')

"""# Add Tree Attributes (Features)"""

for node in t2.traverse("postorder"):
  # print("Node is ", node.name)
  key = "struc"
  if node.is_root():
    stype = "FDH"
    struc = "FDH"
    sss = False
    fcp = 0
    f = "1-864"
    s = 0
    r = 0
    s_act = False
  else:
    stype = df.loc[node.name, "Type"]
    struc = df.loc[node.name, "Struc"]
    sss = df.loc[node.name, "SSS"]
    fcp = df.loc[node.name, "FCP"]
    f = df.loc[node.name, "Fibre"]
    s = df.loc[node.name, "Spare"]
    r = df.loc[node.name, "Reserve"]
    # res =     # FLAG to indicate reserve (no Splice Activity)
    # range_start =
    # range_end = 
    s_act = df.loc[node.name, "Activity"]

  sheet = df.loc[node.name, "SHEET"]
  
  # print("struc: ", struc, )
  node.add_features(struc=struc, sss=sss, sheet=sheet, fcp=fcp, fibre=f, spare=s, reserve=r, splice=s_act)

# node.features
for node in t2.search_nodes(sss="SSS"):
  print(node.name, 
        node.struc, 
        node.sss, 
        node.fibre, 
        node.spare, 
        node.reserve, 
        node.sheet, 
        node.splice)

"""# FSA Verifications"""

nums = df["Number"]
seen = set()
uniq = [x for x in nums if x not in seen and not seen.add(x)]
dupes = [x for x in nums if x in seen or seen.add(x)]
print(dupes, uniq)



print(ete3.__version__)
from ete3 import Tree

t = Tree( "((a,b),c);" )
t.render(file_name="%%inline", w=500) #, units="mm"

ts = TreeStyle()
ts.show_leaf_name = True

def my_layout(node):
  #dont include root
  if not node.is_leaf() and node.up:
    node.add_face(TextFace(node.name), column=1, position='branch-right')
    node.add_face(AttrFace(node.))



import random
import sys

def get_json(node):
    # Read ETE tag for duplication or speciation events
    if not hasattr(node, 'evoltype'):
        dup = random.sample(['N','Y'], 1)[0]
    elif node.evoltype == "S":
        dup = "N"
    elif node.evoltype == "D":
        dup = "Y"

    # node.name = node.name.replace("'", '')
        
    json = { "name": node.name, 
             "display_label": node.name,
             "structure": node.struc,
             "branch_length": str(node.dist),
             "common_name": node.name,
            #  "seq_length": 0,
            #  "type": "node" if node.children else "leaf",
            #  "uniprot_name": "Unknown",
             }
    if node.children:
        json["children"] = []
        for ch in node.children:
            json["children"].append(get_json(ch))
    return json

print(str(get_json(t2)).replace("'", '"'))

