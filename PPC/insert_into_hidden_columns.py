## Used on 2022/05/12 to insert a PPC File with the DNE Column REMOVED, into a PPC file with the DNE Columns Present


import pandas as pd
import numpy as np
import glob
import os
import re

from tkinter.filedialog import askdirectory, askopenfilename
path = askdirectory()

input_path = askopenfilename()
source = pd.read_excel(input_path, header=0)

ppc_path = askopenfilename()
destination = pd.read_excel(ppc_path, sheet_name="PPC", header=1)

result = pd.merge(destination, source, how='left', on="EnceptaID") # one_to_one

## Move all the shit over

result.to_excel(path+"PYTHON_PPC_merged.xlsx", index=None)