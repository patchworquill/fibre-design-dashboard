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
    df.columns = ["Address"] # , "DedicatedFiber"
    
    # Get the header label
    label = df.at[0,"Address"]
    label = str.split(label, " ")
    fcp = label[0] # Typically FCP is first
    df["FCP#"] = fcp
    terminalID = fcp.split("#")[1] #Isolate the number part of the FCP
    df["TerminalID"] = int(label[0].split("#")[1]) # Add column to hold FCP
    df["Structure"] = label[1]
    df["Filename"] = filename
    df["TerminalLocation"] = str(label[-3] +" "+ label[-2] +" "+ label[-1]) # Get the address by joining together the space-split text
    df = df.drop(index=0)
    li.append(df)

lio = []
keys = []

# Merge into single Table
for table in li:
    lio.append(table)
    keys.append(table["Structure"][1])

df = pd.concat(lio, keys=keys)

## Clean up addresses
## TODO: This really needs to be more robust. Just in 1141A, 
#       I have caught errors including: typos, extra whitespace (which the regex below solves), 
#       different Street Type abbreviations, and accidental punctuation characters (at end and start)
df["Address"] = df["Address"].apply(lambda x: re.sub(' +', ' ',x))
df = df.drop(['FCP#'], axis=1)


# Output a folder of CSV Files to import to the PPC Excel
opath = path+"/../Py-OUTPUT/"
exists = os.path.exists(opath)
if not exists:
    os.mkdir(str(opath))

df = df.replace("\P", None)

# TODO: replace all \P Characters

## Export all tables as separate
# for table in lio:
#     outpath = str(opath+table.at[1,"Structure"]+".csv")
#     table["DedicatedFiber"] = int(table["DedicatedFiber"])
#     # with open(outpath, "w+") as file:
#     table.to_csv(outpath, index=False)

## Export combined dataframe to CSV
df.to_csv(opath+"1-df_clean.csv", index=False)
df.to_excel(opath+"1-df_clean.xlsx", index=False)

####################################################
## 
##                  PART 2
## 
##      Read the Splice Annotation Text CSV
##          from Rhino Export to DF
##
####################################################

splice_r_path = askopenfilename(title="Select Terminal Annotation CSV from Rhino Export Step")
splices = pd.read_csv(splice_r_path, header=0, index_col=False, on_bad_lines="skip")
# splices_missing = pd.read_csv(splice_r_path, header=0, index_col=False, on_bad_lines='skip')

splices['TerminalID'] = splices['TerminalID'].replace(np.nan, "0") 
splices["TerminalID"] = splices['TerminalID'].apply(lambda x: int(x.replace("#", "")))

###### MERGING TEST THINGY
dfs = pd.merge(df, splices, how="left", on="TerminalID")
dfs.to_csv(opath+"2-df_splices.csv", index=False)
dfs.to_excel(opath+"2-df_splices.xlsx", index=False)

####################################################
## 
##                  PART 3
## 
##      Import the PPC xlsx file and
##          loop through the 
##
####################################################

## Optionally load the files
# df_path = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3111A\DFD\\Py-OUTPUT\\1-df_clean.csv"
# dfs_path = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3113A\DFD\\Py-OUTPUT\\2-df_splices.csv"
# dfs_path = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3113A\DFD\\Py-OUTPUT\\2-df_splices.xlsx"
# ppc_path =  "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD\\(Premise Data - FMS Tracker) OGDN 1144A 2847101.xlsx"
# opath = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3111A\DFD\\2nd Submission\Py-OUTPUT"

# df = pd.read_csv(df_path)
# dfs = pd.read_csv(dfs_path)
# dfs = pd.read_excel(dfs_path)

ppc_path = askopenfilename(title="Select Output PPC.xlsx File for this FSA (Do NOT use the combined PPC)")
ppc = pd.read_excel(ppc_path, sheet_name=0, header=2) # TODO: if OKRG =1 if PTMS =2

coid = "PTMS"
def safe_concat(n):
    if pd.isna(n):
        return ""
    else:
        # if type(n) is float:
        #     n = int(n)
        return str(str(n) + " ")

fullAddress = []

# PTMS / HANY version
if coid == ("PTMS" or "HANY"):
    for i in range(0, len(ppc)):
        n = ppc["Street Number"][i]
        print(n)
        if type(n) is np.float64:
            if pd.isna(n):
                n=""
                print(i)
            else:
                n = int(n)
                print(n)
        else:
            print("not Float")
            print(type(n))
        # sn = safe_concat(ppc["Street Number"][i])
        sn = safe_concat(n)
        st = safe_concat(ppc["Street Type"][i])
        ds = safe_concat(ppc["Directional Suffix(vector)"][i])
        fullAddress.append( sn + str(ppc["Street Name"][i]) +" "+ st + ds)

fullAddress

# OKRG / OGDN version
if coid == ("OKRG" or "OGDN"):
    for i in range(0, len(ppc)):
        sn = safe_concat(ppc["Street Number"][i])
        st = safe_concat(ppc["Street Type"][i])
        fullAddress.append(sn +" "+ str(ppc["StreetName"][i]) +" "+ st +" "+ str(ppc["Directional Suffix"][i]))

ppc["FullAddress"] = fullAddress

ppc_copy = ppc.copy()

dfs_list = dfs['Address'].tolist()
missing_addresses = []
failed = pd.DataFrame(columns=dfs.columns)

for i in ppc.index.tolist():
    print()
    address = ppc.at[i, "FullAddress"].rstrip()
    print("address: ", address)
    
    if address.lstrip() in dfs_list:
        this_index = dfs_list.index(address)
        print("index: ", i, "dfs index:", this_index)
        this_slice = dfs[dfs['Address']==address]
        print("dfs", this_slice)

        if len(this_slice) > 1:
            if len(failed) == 0:
                failed = failed.merge(this_slice, how="left")
            else:
                failed = failed.merge(this_slice, how="left")

        elif len(this_slice) == 1:
            # Set the columns in ppc directly to match
            # ppc_copy['Sheet No', 'Fibre ID (Terminal ID)','Terminal Location' , 'Fiber Distribution Count', 'Dedicated Fiber'] = this_slice[['SheetNo', 'TerminalID', 'TerminalLocation', 'FiberAllocation', 'DedicatedFiber']]
            ppc_copy.at[i, 'Sheet No'] = this_slice['SheetNo'].values[0]
            ppc_copy.at[i,'Fibre ID (Terminal ID)'] = this_slice['TerminalID'].values[0]
            ppc_copy.at[i, 'Terminal Location'] = this_slice['TerminalLocation_x'].values[0] # TerminalLocation
            ppc_copy.at[i, 'Fiber Distribution Count'] = this_slice['FiberAllocation'].values[0]
            # ppc_copy.at[i, 'Dedicated Fiber'] = this_slice['DedicatedFiber'].values[0]
        else:
            pass
    else:
        missing_addresses.append(address)

ppc_copy.to_excel(opath+"/MERGE_TO_PPC.xlsx", index=None)

####################################################
## 
##                  PART 4
## 
##      Add RESERVE Fibers from Rhino Output
##          
##
####################################################

splice_r_path = askopenfilename(title="Select RESERVE Annotation CSV from Rhino Export Step")
reserves = pd.read_csv(splice_r_path, header=0, index_col=False, on_bad_lines="skip")
# splices_missing = pd.read_csv(splice_r_path, header=0, index_col=False, on_bad_lines='skip')

###### MERGING TEST THINGY
ppc2 = pd.merge(ppc_copy, reserves, how="left", left_on="FullAddress", right_on="TerminalLocation")
ppc2.to_excel(opath+"/MERGE_TO_PPC_res.xlsx", index=None)