base_path = "../../KadTec/DFD/Fiber Layout"
fsa = "1031B"
df_path = "../../KadTec/DFD/Fiber Layout/1031B/1-df_clean.xlsx"
dfs_path = "../../KadTec/DFD/Fiber Layout/1031B/2-df_splices.xlsx"
ppc_path =  "../../KadTec/DFD/Fiber Layout/1031B/(Premise Data - FMS Tracker) OKRG 1031B 2848692New Format.xlsx"
opath = "../../KadTec/DFD/Fiber Layout/1031B/Py-OUTPUT/"

import pandas as pd
import numpy as np

df = pd.read_excel(df_path)
dfs = pd.read_excel(dfs_path)
ppc = pd.read_excel(ppc_path, header=2)

## Join the ppc and df into "result" on Address
fullAddress = []

for i in range(0, len(ppc)):
    fullAddress.append(str(ppc["Street Number"][i]) +" "+ str(ppc["Street Name"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix(vector)"][i])
    # fullAddress.append(str(ppc["Street No"][i]) +" "+ str(ppc["StreetName"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix"][i])

ppc["FullAddress"] = fullAddress

# Check Addresses
ppc[["Unit Number", "Street Number", "Street Name", "Street Type", "Directional Suffix(vector)", "FullAddress"]]

ppc_sfu = ppc[ppc['MDU, MTU, SFU, SBU']=="SFU"]
sfu = ppc_sfu[ppc_sfu["Unit Number"].isnull()]
bsmt = ppc_sfu[ppc_sfu["Unit Number"]=="BSMT"]

bsmt_result = pd.merge(bsmt, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many")
main_result = pd.merge(sfu, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many")

## Create a big for loop to loop through the shit and fit it back into the original PPC file format
result = pd.merge(ppc_sfu, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_one") # one_to_one validate="one_to_many"
result.to_excel(opath+"PYTHON_PPC-step-2.xlsx", index=None)

ppc_copy = ppc.copy()

dfs_list = dfs['Address'].tolist()

for i in ppc.index.tolist():
    print("index: ", i)

    address = ppc.at[i, "FullAddress"]

    print("address: ", address)
    failed = 0
    if address in dfs_list:
        this_index = dfs_list.index(address)
        print("dfs index:", this_index)
        this_slice = dfs[dfs['Address']==address]
        print("dfs", this_slice)

        if len(this_slice) > 1:
            if failed == 0:
                failed = this_slice
            else:
                failed = failed.join(this_slice)

        elif len(this_slice) == 1:
            # Set the columns in ppc directly to match
            # ppc_copy['Sheet No', 'Fibre ID (Terminal ID)','Terminal Location' , 'Fiber Distribution Count', 'Dedicated Fiber'] = this_slice[['SheetNo', 'TerminalID', 'TerminalLocation', 'FiberAllocation', 'DedicatedFiber']]
            ppc_copy.at[i, 'Sheet No'] = this_slice['SheetNo']
            ppc_copy.at[i,'Fibre ID (Terminal ID)'] = this_slice['TerminalID']
            ppc_copy.at[i, 'Terminal Location'] = this_slice['TerminalLocation']
            ppc_copy.at[i, 'Fiber Distribution Count'] = this_slice['FiberAllocation']
            ppc_copy.at[i, 'Dedicated Fiber'] = this_slice['DedicatedFiber']
        else:
            pass

ppc_copy.to_excel(opath+"loop-test.xlsx", index=None)
    

    
