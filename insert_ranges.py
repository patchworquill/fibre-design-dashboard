ranges_file = "K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\\1031B Fiber design_RANGES.csv" 

if os.path.exists(ranges_file):
    if os.path.isfile(ranges_file):
        try:
            ranges_df = pd.read_csv(ranges_file, header=0)
            print("Loaded ")
        except Exception as e:
            print("Failed to load ", e)
        finally:
            print(" file:", ranges_file)

file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\(Fibre Data) OKRG 1031B.xlsx'
nodes_df = pd.read_excel(file, sheet_name="Node", header=0)
nodes_df = nodes_df.drop("HSDP", axis=1)
edges_df = pd.read_excel(file, sheet_name="Wire", header=0)

ranges_df = ranges_df[["STRUCTURE","LIVE","SPARE","HSDP_start","HSDP_end","SPARE_start","SPARE_end","HSDP","SPARE"]]

# MERGE
result = pd.merge(nodes_df, ranges_df, how='left', left_on=['NODE'], right_on=["STRUCTURE"], validate="one_to_one")
result.to_excel("./(FIBRE DATA) RANGES.xlsx", index=None)

nodes_df["NODE"]
for i in ranges_df["STRUCTURE"]