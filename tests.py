import calculations
import plask
import pandas as pd
import json
import time
import numpy as np
def load_case(self,overwrites, index : int):


            
    unformatted_dict = overwrites.iloc[index].to_dict()
    defs = {x : unformatted_dict[x] for x in unformatted_dict}
    defs['n_top_dbr'] = int(defs['n_top_dbr'])
    defs['n_bottom_dbr'] = int(defs['n_bottom_dbr'])
    plask.loadxpl(xpl_path,destination=locals(),defs=defs)

xlsx_path = "test_data.xlsx"
xpl_path = "tutorial3.xpl"
overwrites : pd.DataFrame = pd.read_excel(xlsx_path)

overwrites['n_top_dbr'] = pd.to_numeric(overwrites['n_top_dbr'],downcast='integer',errors='coerce')
overwrites['n_bottom_dbr'] = pd.to_numeric(overwrites['n_bottom_dbr'],downcast='integer',errors='coerce')

try:
    print("Loaded Previous")
    with open("test.json",'r') as file:
        results = json.loads(file.read())
except:
    print("Failed to load")
    results = []

lam0 = 900
lamn = 980
n_mode_space = 1601
m_list = list(range(100))

start_time = time.time()

for i in range(overwrites.shape[0]):
            
    unformatted_dict = overwrites.iloc[i].to_dict()
    defs = {x : unformatted_dict[x] for x in unformatted_dict}
    defs['n_top_dbr'] = int(defs['n_top_dbr'])
    defs['n_bottom_dbr'] = int(defs['n_bottom_dbr'])
    case_info = overwrites.iloc[i].to_dict()
    plask.loadxpl(xpl_path,defs=defs)

    lams = np.linspace(lam0,lamn,n_mode_space)


    m_potential_modes = []
    for m in m_list:

        dets = np.abs(SOLVER.optical.get_determinant(lams,m))
        dets_filtered_left = -dets[1:-1] + dets[:-2]
        dets_filtered_right = -dets[1:-1] + dets[2:]
        dets_filtered =np.bitwise_and( (dets_filtered_left > 0),  (dets_filtered_right > 0))
        lam_modes = lams[1:-1][dets_filtered]
        m_potential_modes.append((m,lam_modes))

    # m_modes = list_optical_modes(m_potential_modes)
    case_results = []

    for m,potential_modes in m_potential_modes:
        potential_modes = list(potential_modes)
        for mode_i in range(len(potential_modes)):
            for vmin,vmax in [(v/2,v/2+0.5) for v in range(0,6)]:

                potential_mode = potential_modes[mode_i]
                
                print(m,potential_mode,vmax)


                SOLVER.optical.lam0 = potential_mode
                SOLVER.maxlam = (potential_modes+[980])[mode_i+1]
                SOLVER.lpm = m
                SOLVER.vmax = vmax
                #if compute fails then that means that the required voltage is too high
                # figure out how to get the max voltage reacheds
                try:
                    V = SOLVER.compute()
                    
                    I = SOLVER.threshold_current
                    lams = []

                    print(len(SOLVER.outWavelength))
                    for i in range(len(SOLVER.outWavelength)):
                        lam = SOLVER.outWavelength(i)
                        lams.append(lam)

                    print(f"Found mode m {m} lam {lams} V {V} I {I}")
                    case_results.append({'m' : m,'lam' : lams, 'voltage' : V, 'current' : I})
                    
   
                    break
                except Exception as e:
                    print(e)
                    pass
    case_info['case_results'] = case_results

    results.append(case_info)

    print(f"case {i} took {(time.time() - start_time)/60} minutes")
    start_time = time.time()
    with open("test.json",'w') as file:
        file.write(json.dumps(results))