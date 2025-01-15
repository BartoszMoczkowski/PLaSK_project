import plask
import pandas as pd
import json
import time
import numpy as np

xlsx_path = "test_data.xlsx"
xpl_path = "tutorial3.xpl"
overwrites : pd.DataFrame = pd.read_excel(xlsx_path)

overwrites['n_top_dbr'] = pd.to_numeric(overwrites['n_top_dbr'],downcast='integer',errors='coerce')
overwrites['n_bottom_dbr'] = pd.to_numeric(overwrites['n_bottom_dbr'],downcast='integer',errors='coerce')
overwrites['mesa'] = pd.to_numeric(overwrites['mesa'],downcast='integer',errors='coerce')

n_done = 0
try:
    print("Loaded Previous")
    with open("test.json",'r') as file:
        results = json.loads(file.read())

    for x in results:
        if x['id'] > n_done:
            n_done = int(x["id"])
except:
    print("Failed to load")
    results = []
lam0 = 900
lamn = 980
n_mode_space = 1601
m_list = list(range(100))

start_time = time.time()
skip_list = []
for i in range(n_done,overwrites.shape[0]):
    
    if i in skip_list:
        continue
    print(f"CASE : {i+1}")

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
    found_modes = []

    for m,potential_modes in m_potential_modes:
        potential_modes = list(potential_modes)
        for mode_i in range(len(potential_modes)):
            potential_mode = potential_modes[mode_i]
            try:
                ko = SOLVER.optical.find_mode(potential_mode,m=m)
                print(SOLVER.optical.modes[ko])
            except Exception as e:
                print(f"m {m} potential_mode {potential_mode} failed {e}")
                continue
            

            skipable = False
            for prev_mode in found_modes:
                if abs(prev_mode-potential_mode) <= 0.2:
                    skipable = True
            
            if skipable:
                print("Mode already found. Skipping")
                continue
            
            for vmin,vmax in [(v/2,v/2+0.5) for v in range(2,10)]:

                

                print(m,potential_mode,vmax)


                SOLVER.optical.lam0 = potential_mode
                SOLVER.maxlam = (potential_modes+[980])[mode_i+1]
                SOLVER.lpm = m
                # SOLVER.vmin = vmin
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
                        found_modes.append(lam)
                        found_modes.append(potential_mode)

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