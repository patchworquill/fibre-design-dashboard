import pandas as pd
import numpy as np
import glob
import os
import re

import tkinter
from tkinter.filedialog import askdirectory, askopenfilename

# Load RhinoData sheet
datafile = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\HANY 2093B\R\Rhino_Data.xlsx"
opath = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\HANY 2093B\R\Table Export\\"

print(os.path.exists(datafile))
if not os.path.exists(opath):
    os.mkdir(opath)

sheet = "drops"
df = pd.read_excel(datafile,sheet_name=sheet, header=0)
df = df.drop(["Unnamed: 12","Unique FCPs", "Unique Ranges", "Unique MPTs"], axis=1)

for mpt in df['MPT Location'].tolist():
    table = []
    slice = df[df['MPT Location']==mpt]
    header = slice['TABLE HEADER'].tolist()[0]
    print(header)
    # table.append(header)
    for address in slice["FullAddress"].tolist():
        table.append(address)
    t1 = pd.DataFrame(table)
    t1.columns = [header]
    t1 = t1.sort_values(by=[header])
    t1
    t1.to_csv(opath+mpt+".csv", header=True, index=None)
