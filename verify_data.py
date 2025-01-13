import plask
import pandas as pd


DATA_TO_TEST = "test_data.xlsx"


xpl_path = "tutorial3.xpl"
overwrites : pd.DataFrame = pd.read_excel(DATA_TO_TEST)

overwrites['n_top_dbr'] = pd.to_numeric(overwrites['n_top_dbr'],downcast='integer',errors='coerce')
overwrites['n_bottom_dbr'] = pd.to_numeric(overwrites['n_bottom_dbr'],downcast='integer',errors='coerce')

failed_cases = []
for i in range(overwrites.shape[0]):
            
    unformatted_dict = overwrites.iloc[i].to_dict()
    defs = {x : unformatted_dict[x] for x in unformatted_dict}
    defs['n_top_dbr'] = int(defs['n_top_dbr'])
    defs['n_bottom_dbr'] = int(defs['n_bottom_dbr'])
    case_info = overwrites.iloc[i].to_dict()
    try:
        plask.loadxpl(xpl_path,defs=defs)
    except Exception as e:
        print(e)
        print(f"Failed to load case {i}")
        failed_cases.append((i,e))

print(f"failed to load cases {failed_cases}")
