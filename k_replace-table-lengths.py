import pandas as pd
import numpy as np
import glob

from tkinter.filedialog import askdirectory
path=askdirectory()

## LOAD THE TABLES CSVs FROM THE DWG
all_files = glob.glob(path + "/*.csv")

li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    df.columns = ["ACTIVITY #", "No #", "SIZE/TYPE", "LENGTH", "Z-COORDINATES"]
    df = df[df["ACTIVITY #"] != "XXX-X"]
    df["TABLE"] = filename
    li.append(df)

df = pd.concat(li, axis=0, ignore_index=True)

print("\nFILES LOADED:\n")
for file in all_files:
    print("\t",file)

## LOAD THE NEW LENGTH CSVs FROM RHINO ANALYSIS STAGE
##      These are created using a program called topology_to_tree-numbers_600-annotation_ADDING-LENGTH
path_lengths=askdirectory()
length_files = glob.glob(path_lengths + "/*.csv")

li = []
for filename in length_files:
    df2 = pd.read_csv(filename, index_col=None, header=0)
    df2.columns = ["ACTIVITY #", "LENGTH"]
    df2["File"] = filename
    li.append(df2)

print("\nLENGTH FILES LOADED:\n")
for file in length_files:
    print("\t",file)

## FIND the Activity Number in the Tables, and Insert it into the new Tables
for update_record in range(0, len(df2)):
    ## TODO: only update if not the same!
    ac = df2.iloc[update_record]["ACTIVITY #"] 
    new_length = int(np.ceil(df2.iloc[update_record]["LENGTH"])) ## Round up the length to the nearest meter
    
    if new_length != df.at[id, "LENGTH"]:
    ## Print a list of the changes
        print("Activity: ",ac,"\tOLD\t",str(df[df["ACTIVITY #"]==str(ac)].LENGTH.values[0]),"\tNEW:\t",str(new_length),"m")
        # df[df["ACTIVITY #"]==str(ac)].LENGTH.values[0] = str(str(new_length)+"m")
        id = df.index[df["ACTIVITY #"]==str(ac)].tolist()[0]
        df.at[id, "LENGTH"] = str(str(new_length)+"m")
    else:
        print("NO CHANGE:",new_length,df.at[id, "LENGTH"])

ac = 620
df[df["ACTIVITY #"]==str(ac)]
id = df.index[df["ACTIVITY #"]==str(ac)].tolist()[0]
id+1
df.loc[id]
new_length = 140
df.loc["LENGTH", df["ACTIVITY #"]==str(ac)] = str(str(new_length)+"m")

len(df2)

## Output the Updated Tables to the CSV Files!

