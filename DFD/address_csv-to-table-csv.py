import pandas as pd
import os

file = "K:\Clients\AFL - AFL\\2022\\003 - HANY - PTMS - 2022\PTMS 3113A\DFD\R\\addresses.csv"
opath = "K:\Clients\AFL - AFL/2022/003 - HANY - PTMS - 2022\PTMS 3113A\DFD\Py-OUTPUT/Address Tables/"
if not os.path.exists(opath):
    os.mkdir(opath)

df = pd.read_csv(file, header=None)
df.columns = ["Address", "Struc", "Distance"]

strucs = df['Struc'].unique().tolist()
for struc in strucs:
    this = df[df["Struc"] ==struc]
    ad = this['Address']
    if (len(ad) > 0):
        table_header = pd.Series("FCP#xxxxx "+struc+" \PF"+ad[ad.index[0]])
        ad = pd.concat([table_header, ad])
        ad.to_csv(opath+"\\"+struc+".csv", header=None, index=None)