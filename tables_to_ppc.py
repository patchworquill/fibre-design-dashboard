import pandas as pd
import numpy as np
import glob
import os
import re

import tkinter
from tkinter.filedialog import askdirectory, askopenfilename

## Attempt to put the file dialog window in front... https://stackoverflow.com/questions/3375227/how-to-give-tkinter-file-dialog-focus
root = tkinter.Tk()
root.withdraw()
root.lift()
root.focus_force()
path=askdirectory(title="Select AutoCAD Table Export CSV Folder", parent=root)

all_files = glob.glob(path + "/*.csv")

####################################################
## 
##                  PART 1
## 
## Import the AutoCAD tables from csv to dataframes
##
####################################################

li = [] # li is a list full of dataframes. One for each table as exported from AutoCAD

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=None)
    df.columns = ["Address", "DedicatedFiber"]
    
    # Get the test
    label = df.at[0,"Address"]
    label = str.split(label, " ")
    fcp = label[0]
    df["FCP#"] = fcp
    terminalID = fcp.split("#")[1]
    df["TerminalID"] = label[0].split("#")[1] # Add column to hold FCP
    df["Structure"] = label[-1]
    df["Filename"] = filename
    df = df.drop(index=0)
    li.append(df)

####################################################
## 
##                  PART 2
## 
##      Create the FibreAllocation Ranges
##
####################################################

lio = []
keys = []

# Calculate FibreAllocation
for table in li:
    # TODO: add extra if fibre is a range
        #   Traceback (most recent call last):
        #     File "K:\Personal Files\Patrick Wilkie\Design + Engineering\Python\tables_to_ppc.py", line 58, in <module>
        #       minF = str(int(table["DedicatedFiber"].min()))
        #   ValueError: invalid literal for int() with base 10: '181-182'
    try:
        fx = table["DedicatedFiber"].split("-")[0]
    except Exception as e:
        print(e)
        fx = table["DedicatedFiber"]
    minF = str(int(fx.min()))
    maxF = str(int(fx.max()))
    print("min", minF, " Max: ", maxF)
    table["FibreAllocation"] = str(minF+"-"+maxF)
    lio.append(table)
    keys.append(table["Structure"][1])

df = pd.concat(lio, keys=keys)

## Clean up addresses
## TODO: This really needs to be more robust. Just in 1141A, 
#       I have caught errors including: typos, extra whitespace (which the regex below solves), 
#       different Street Type abbreviations, and accidental punctuation characters (at end and start)
df["Address"] = df["Address"].apply(lambda x: re.sub(' +', ' ',x))
# df.reset_index()

# Verify the FibreAllocation ranges
# print([table["FibreAllocation"] for table in lio])

# Output a folder of CSV Files to import to the PPC Excel
opath = path+"/OUTPUT/"
exists = os.path.exists(opath)
if not exists:
    os.mkdir(str(opath))

## Export all tables as separate
# for table in lio:
#     outpath = str(opath+table.at[1,"Structure"]+".csv")
#     table["DedicatedFiber"] = int(table["DedicatedFiber"])
#     # with open(outpath, "w+") as file:
#     table.to_csv(outpath, index=False)

## Export combined dataframe to CSV
df.to_csv(opath+"PYTHON_PPC-step-1.csv", index=False)
df.to_excel(opath+"PYTHON_PPC-step-1.xlsx", index=False)

####################################################
## 
##                  PART 3
## 
##      Read the Excel PPC File to a Dataframe
##
####################################################

ppc_path = askopenfilename(title="Select Output PPC.xlsx File for this FSA (Do NOT use the combined PPC)")
xl = pd.ExcelFile(ppc_path)

for i, sheet in enumerate(xl.sheet_names):
    print(i, ":", sheet)
# print(xl.sheet_names)  # see all sheet names
sheet_name = int(input("Select sheet with PPC data:"))
sheet_name = xl.sheet_names[sheet_name]
ppc = xl.parse(sheet_name, header=1)  # read a specific sheet to DataFrame
# ppc = pd.read_excel(ppc_path, sheet_name="OKRG", header=1) # sheet_name="PPC" | "OKRG"

# Filter out all DNE properties
# ppc = ppc[ppc["DoesNotExist"]==False] ## TODO: Change this line -- it causes headache later in the process!
# ppc = ppc.reset_index()

# Set the data in the columns
ppc["DropDesign"] = "Conduit"
ppc["DistributionDesign"] = "Conduit"

# Set the FSA variable data
ppc["TerminalID"] = terminalID

# Get the addresses, which will act as keys for the table join (AutoCAD DFD Tables to PPC)
fullAddress = []
for i in range(0, len(ppc)):
    fullAddress.append(str(ppc["Street Number"][i]) +" "+ str(ppc["Street Name"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix(vector)"][i])
    # fullAddress.append(str(ppc["Street No"][i]) +" "+ str(ppc["StreetName"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix"][i])

ppc["FullAddress"] = fullAddress
# ppc["TerminalID"][i] = df[]

# From the pandas documentation: https://pandas.pydata.org/docs/user_guide/merging.html
# We want to perform an inner join on the data. In reality, we want the tables from AutoCAD and the PPC table to be exactly corresponding in number of rows.
result = pd.merge(ppc, df, how='left', left_on=['FullAddress'], right_on=['Address']) # one_to_one validate="one_to_many"
result.to_excel(opath+"PYTHON_PPC-step-2.xlsx", index=None)

## MATCH A SUBSTRING
# df.loc[df["Address"].str.contains("CO", case=False)]
# df.loc[df["Address"].str.contains("5 RIVERGLEN CL SE", case=False)]
# df.replace()

####################################################
## 
##                  PART 4
## 
##      Read the Splice Annotation Text CSV
##          from Rhino Export to DF
##
####################################################

## df["Structure"] or df["TerminalID"]
splice_r_path = askopenfilename(title="Select Splice Annotation CSV from Rhino Export Step")
splices = pd.read_csv(splice_r_path, header=0, index_col=False)
# splices.columns = ["TerminalID", "TerminalLocation", "FSA", "FiberAllocation", "SheetNo"]

splices["TerminalID"] = splices['TerminalID'].apply(lambda x: x.replace("#", ""))

## Fixing for TerminalID_y contains NaNs
rx = result['TerminalID_y'].replace(np.nan, 0).astype(int)  
result = result.merge(splices, left_on=rx, right_on="TerminalID")

result2 = pd.merge(result, splices, how='left', left_on=rx, right_on=['TerminalID']) # one_to_one
result2.to_excel(opath+"PYTHON_PPC_step-4_validate.xlsx", index=None)

# Set the Structure variable data
# TODO:
# ppc["Sheet No"]
# ppc["FiberAllocation"]

## Testing a different approach: how = inner:
# result = pd.merge(ppc, df, how='inner', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many") # one_to_one
# result = pd.merge(result, splices, how='inner', left_on=['TerminalID_y'], right_on=['TerminalID']) # one_to_one
# result.to_excel(opath+"PYTHON_PPC_inner.xlsx", index=None)

# result = pd.merge(ppc, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many") # one_to_one
# result = pd.merge(result, splices, how='inner', left_on=['TerminalID_y'], right_on=['TerminalID']) # one_to_one
# result.to_excel(opath+"PYTHON_PPC_left-inner.xlsx", index=None)