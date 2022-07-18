import pandas as pd
import numpy as np
import pathlib, os

# Kadtec
base_path = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3113A\DFD\R"
coid = "PTMS"
fsa = "3113A"
opath = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3113A\DFD\Py-OUTPUT"





if not os.path.exists(opath):
    os.mkdir(opath)




## If excel files (Data Format)
# base_path = pathlib.Path(base_path)
# datapath = pathlib.Path.joinpath(base_path, "(Fibre Data) "+coid+" "+fsa+".xlsx")
addresses = pd.read_excel(str(datapath), sheet_name="Addresses")
structures = pd.read_excel(str(datapath), sheet_name="Structures")
sheets = ['Splice Types', 'Node', 'Addresses', 'Wire', 'MPT Tails', 'Text']

## If CSV files
address_path = str(base_path + "\\" + "addresses.csv")
structure_path = str(base_path + "\\" + "structures.csv")
addresses = pd.read_csv(address_path, header=None)
addresses.columns = ['Address', 'Structure', 'x', 'y']
structures = pd.read_csv(structure_path, header=None)
structures.columns = ["STRUCTURE-ID"]

structures['FiberCount'] = 0

for s in structures['STRUCTURE-ID']:
    count = len(addresses[addresses['Structure']==s])
    s_id = structures[s, 'STRUCTURE-ID']
    print(s, count)
    structures.at[s, 'FiberCount'] = count 

structures['FiberCount'] = 
counts = addresses.groupby(by=['Structure']).count()
counted = structures.merge(counts, how="left", left_on='STRUCTURE-ID', right_on=counts.index)

counted.to_excel(opath+"\counts.xlsx", index=None)