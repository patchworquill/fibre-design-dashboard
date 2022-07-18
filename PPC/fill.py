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
    df["TerminalID"] = int(label[0].split("#")[1]) # Add column to hold FCP
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
        # print(e)
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
df = df.drop(['FCP#'], axis=1)
# df.reset_index()

# Verify the FibreAllocation ranges
# print([table["FibreAllocation"] for table in lio])

# Output a folder of CSV Files to import to the PPC Excel
opath = path+"/../Py-OUTPUT/"
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
df.to_csv(opath+"1-df_clean.csv", index=False)
df.to_excel(opath+"1-df_clean.xlsx", index=False)

####################################################
## 
##                  PART 3
## 
##      Read the Splice Annotation Text CSV
##          from Rhino Export to DF
##
####################################################

splice_r_path = askopenfilename(title="Select Splice Annotation CSV from Rhino Export Step")
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
##                  PART 4
## 
##      Read the Excel PPC File to a Dataframe
##
####################################################

ppc_path = askopenfilename(title="Select Output PPC.xlsx File for this FSA (Do NOT use the combined PPC)")
# xl = pd.ExcelFile(ppc_path)

# for i, sheet in enumerate(xl.sheet_names):
#     print(i, ":", sheet)
# # print(xl.sheet_names)  # see all sheet names
# sheet_name = int(input("Select sheet with PPC data:"))
# sheet_name = xl.sheet_names[sheet_name]

ppc_raw = pd.read_excel(ppc_path, sheet_name=0, header=2)
# ppc_raw = xl.parse(sheet_name=0, header=2)  # read 1st sheet to DataFrame 
ppc = ppc_raw
dne = ppc[ppc['Does Not Exist']==1]
ppc = ppc.drop(dne.index, axis=0)
# ppc = pd.read_excel(ppc_path, sheet_name="OKRG", header=1) # sheet_name="PPC" | "OKRG"

# Filter out all DNE properties
# ppc = ppc[ppc["DoesNotExist"]==False] ## TODO: Change this line -- it causes headache later in the process!
# ppc = ppc.reset_index()

# TODO: properly filter DNE properties

# TODO: This is broken for HANY, need to update so that it actually pulls / references a column or attribute in the DataFile
# Set the data in the columns
ppc['DESIGN Bus count'] = ppc['PPC Bus Count']
ppc['DESIGN Res count'] = ppc['PPC Res Count']
ppc["Drop (aerial, conduit, aerial+conduit, Lateral)"] = "Conduit"
ppc["Distribution  (aerial, conduit or direct buried)"] = "Conduit"

# Set the FSA variable data
# ppc["TerminalID"] = terminalID

# Get the addresses, which will act as keys for the table join (AutoCAD DFD Tables to PPC)
fullAddress = []
if 'Street No' in ppc.columns:
    ppc_v = 0
elif 'Street Number' in ppc.columns:
    ppc_v = 1

for i in ppc.index:
    if ppc_v == 0:
        fullAddress.append(str(ppc["Street No"][i]) +" "+ str(ppc["StreetName"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix"][i])
    elif ppc_v == 1:
        fullAddress.append(str(ppc["Street Number"][i]) +" "+ str(ppc["Street Name"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix(vector)"][i])
    else:
        print("AFL Likely Updated the Column Headers yet again. Update the python script with the appropriate headers.")

ppc["FullAddress"] = fullAddress


#### DIFF THE ppc_raw and ppc (after "FullAddress")
ppc.compare(ppc_raw)


# From the pandas documentation: https://pandas.pydata.org/docs/user_guide/merging.html
# We want to perform an inner join on the data. In reality, we want the tables from AutoCAD and the PPC table to be exactly corresponding in number of rows.

# resulta = pd.merge(ppc, df, how='left', left_on=['FullAddress'], right_on=['Address'],) # one_to_one validate="one_to_many"

result = pd.merge(ppc, dfs, how='left', left_on=['FullAddress'], right_on=['Address'], sort=False,) # one_to_one validate="one_to_many"



# Add BSMT conde!!!!
ppc_bsmt = ppc[ppc['Unit Number']=="BSMT"] # BSMT in PPC
df_bsmt = df[df['Address'].str.contains("BSMT")] # BSMT in DF
df_bsmt['Address'].str.replace("/BSMT", "")
df.drop(df_bsmt.index)
ppc_bsmt = pd.merge(ppc_bsmt, df, how='left', left_on=['FullAddress'], right_on=['Address'])




# Add back in DNEs
result = result.append(dne)    

result.reindex_like(ppc)

result = result.reindex(result.index.sort_values())
result.to_excel(opath+"3-ppc_dfs_clean.xlsx", index=None)


source = result
destination = ppc_raw
result = pd.merge(destination, source, how='left', on="Encepta ID") # one_to_one

## Move all the shit over

result.to_excel(opath+"\merged.xlsx", index=None)





## Fixing for TerminalID_y contains NaNs
rx = result['TerminalID_y'].replace(np.nan, 0).astype(int) 
result = result.merge(splices, left_on=rx, right_on="TerminalID")
result.to_excel(opath+"PYTHON_PPC_step-3_validate.xlsx", index=None)

# Copy to columns and Drop
result['DESIGN Bus count'] = result['PPC Bus Count']
result['DESIGN Res count'] = result['PPC Res Count']
result['Fibre ID (Terminal #)'] = result['TerminalID_y']
result['Drop (aerial, conduit, aerial+conduit, Lateral)'] = "conduit"
result['Distribution  (aerial, conduit or direct buried)'] = "conduit"
result['Terminal Location'] = result['TerminalLocation']
result['Fiber Distribution count'] = result['FibreAllocation']
result['dedicated fiber '] = result['DedicatedFiber']
result['Sheet#'] = result["SheetNo"]

final_result = result.drop(['DropDesign', 'DistributionDesign', 'TerminalID_x', 'FullAddress', 'Address', 'DedicatedFiber', 'FCP#', 'TerminalID_y', 'Structure', 'Filename', 'TerminalID', 'FibreAllocation', 'TerminalID', 'TerminalLocation', 'FSA_y', 'FiberAllocation', 'SheetNo'], axis=1)
final_result.to_excel(opath+"PYTHON_PPC_final.xlsx", index=None)



####################################################
## 
##                  PART 5
## 
##      Collate the filled data into the 
##              PPC Spreadsheet
##
####################################################

final_table = pd.merge(ppc, final_result, how='left', on="Encepta ID") # one_to_one

## Move all the shit over

final_table.to_excel(opath+"/merged.xlsx", index=None)

print("Complete! Review step-3 for correctness, and copy from 'merged'")