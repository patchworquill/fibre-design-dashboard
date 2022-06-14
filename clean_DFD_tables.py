import pandas as pd

import tkinter
from tkinter.filedialog import askdirectory, askopenfilename
from os import listdir

##### LOAD DATASHEET
df_path = askopenfilename(title="Select Fibre Data excel file:")
xl = pd.ExcelFile(df_path)

for i, sheet in enumerate(xl.sheet_names):
    print(i, ":", sheet)
sheet_name = int(input("Select sheet with Fibre Node data: "))
sheet_name = xl.sheet_names[sheet_name]
df = xl.parse(sheet_name, header=0)  # read a specific sheet to DataFrame

df = df.set_index('NODE')


##### LOAD ALL CSVs
csv_path = askdirectory(title="Select folder with Rhino CSV Table Export:")
csv_list = listdir(csv_path)
d = {}
for x in range(0, len(csv_list)):
  csv_file = csv_path +"/" + csv_list[x]
  data = pd.read_csv(csv_file, header=None)
  d["{0}".format(data.at[0, 0])] = data

# Create a copy
d2 = d

#### Associate the Struc to the HSDP Range (HSDP_start, HSDP_end)
for s in d:
    print(s)
    if ("FDH" in s) or ("SV" in s) or ("PB" in s):
        print(s)
        pass
    # elif ("PED" in s):
    #     print(s)
    #     pass
    else:
        this = df[df["Struc"]==s]                  
        this_fcp = round(this["FCP"].values[0])
        this_start = round(this["HSDP_start"].values[0])
        this_end = round(this["HSDP_end"].values[0])
        text = str("FCP#"+str(this_fcp)+" HARD-SPLICE DROPS IN SPLICE TRAYS AT "+str(s))

        print(text, "\nS: ", this_start, "E:", this_end)

        droplist = list(range(this_start, this_end+1))
        droplist.insert(0, None)

        d2[s][0][0] = text
        ## Insert into new dictionary (BROKEN METHOD)
        for i, drop in enumerate(droplist):
            d2[s][1] = droplist[:len(d2[s])]

        # TODO: create all the drop ranges

## TODO: save d2 to an excel file