# Macbook
# base_path = "../../KadTec/DFD/Fiber Layout"
# fsa = "1031B"
# df_path = "../../KadTec/DFD/Fiber Layout/1031B/1-df_clean.xlsx"
# dfs_path = "../../KadTec/DFD/Fiber Layout/1031B/2-df_splices.xlsx"
# ppc_path =  "../../KadTec/DFD/Fiber Layout/1031B/(Premise Data - FMS Tracker) OKRG 1031B 2848692New Format.xlsx"
# opath = "../../KadTec/DFD/Fiber Layout/1031B/Py-OUTPUT/"

import pandas as pd
import numpy as np

# Kadtec
coid = "OGDN" # "OGDN" "HANY" "PTMS"
base_path = "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD"
fsa = "1144A"
df_path = "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD\\Py-OUTPUT\\1-df_clean.xlsx"
dfs_path = "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD\\Py-OUTPUT\\2-df_splices.xlsx"
ppc_path =  "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD\\(Premise Data - FMS Tracker) OGDN 1144A 2847101.xlsx"
opath = "K:\Clients\AFL - AFL\\2021\\022 - OGDN\OGDN 1144A\DFD\\Py-OUTPUT"

df = pd.read_excel(df_path)
dfs = pd.read_excel(dfs_path)
ppc = pd.read_excel(ppc_path, header=1)

## Join the ppc and df into "result" on Address
fullAddress = []

for i in range(0, len(ppc)):
    # PTMS / HANY version
    if coid == ("PTMS" or "HANY"):
        fullAddress.append(str(ppc["Street Number"][i]) +" "+ str(ppc["Street Name"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix(vector)"][i])
    # OKRG / OGDN version
    if coid == ("OKRG" or "OGDN"):
        fullAddress.append(str(ppc["Street No"][i]) +" "+ str(ppc["StreetName"][i]) +" "+ ppc["Street Type"][i] +" "+ ppc["Directional Suffix"][i])

ppc["FullAddress"] = fullAddress

# # Check Addresses
# #HANY
# ppc[["Unit Number", "Street Number", "Street Name", "Street Type", "Directional Suffix(vector)", "FullAddress"]]
# # OKRG / OGDN
# ppc[["Unit No", "Street No", "StreetName", "Street Type", "Directional Suffix", "FullAddress"]]

# # HANY
# ppc_sfu = ppc[ppc['MDU, MTU, SFU, SBU']=="SFU"]
# sfu = ppc_sfu[ppc_sfu["Unit Number"].isnull()]
# bsmt = ppc_sfu[ppc_sfu["Unit Number"]=="BSMT"]

# # OKRG / OGDN
# ppc_sfu = ppc[ppc['Premise Type PPC']=="SFU"]
# sfu = ppc_sfu[ppc_sfu["Unit No"].isnull()]
# bsmt = ppc_sfu[ppc_sfu["Unit No"]=="BSMT"]

# bsmt_result = pd.merge(bsmt, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many")
# main_result = pd.merge(sfu, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_many")

# ## Create a big for loop to loop through the shit and fit it back into the original PPC file format
# result = pd.merge(ppc_sfu, df, how='left', left_on=['FullAddress'], right_on=['Address'], validate="one_to_one") # one_to_one validate="one_to_many"
# result.to_excel(opath+"PYTHON_PPC-step-2.xlsx", index=None)









ppc_copy = ppc.copy()

dfs_list = dfs['Address'].tolist()
missing_addresses = []
failed = pd.DataFrame(columns=dfs.columns)

for i in ppc.index.tolist():
    print()

    address = ppc.at[i, "FullAddress"]

    print("address: ", address)
    
    if address in dfs_list:
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
            ppc_copy.at[i, 'Terminal Location'] = this_slice['TerminalLocation'].values[0]
            ppc_copy.at[i, 'Fiber Distribution Count'] = this_slice['FiberAllocation'].values[0]
            ppc_copy.at[i, 'Dedicated Fiber'] = this_slice['DedicatedFiber'].values[0]
        else:
            pass
    else:
        missing_addresses.append(address)

ppc_copy.to_excel(opath+"/loop-test.xlsx", index=None)


    
