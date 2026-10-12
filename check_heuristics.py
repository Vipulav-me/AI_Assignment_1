"""
for every heuristic in HEURISTICS and every one of the 181,440 solvable states:
  inadmissible_states : states where h(s) > h*(s) (overestimates)
  inconsistent_edges : directed edges s -> s2 with h(s) > 1 + h(s2)
  mean_h_over_hstar  : mean of h(s)/h*(s) over all s != GOAL,
this func returns:
  heuristic_checks.csv heuristic, inadmissible_states, inconsistent_edges, mean_h_over_hstar
  heuristic_bands.csv mean h/h* per depth band 1-10, 11-20, 21-31
  heuristic_ratios.csv.gz  per-state h/h* 
"""
import csv
import gzip
from heuristics import HEURISTICS
from oracle import load_true_distance
from puzzle import GOAL, successors
BANDS = [(1,10),(11,20),(21,31)]

def band_of(d):
    for low, high in BANDS:
        if low <= d <= high:
            return f"{low}-{high}"
    return None

def check(h,table):

    #This function returns (inadmissible,inconsistent,{state:h/h*}) for heuristic h.
    hv = {s: h(s) for s in table}
    inadmissible = inconsistent = 0
    ratios = {}
    for s,d in table.items():
        hs = hv[s]
        if hs > d:
            inadmissible += 1
        for s2 in successors(s):
            if hs > 1 + hv[s2]:
                inconsistent += 1
        if s != GOAL:
            ratios[s] = hs/d
    return inadmissible,inconsistent,ratios

def main():
    table = load_true_distance()
    states = [s for s in table if s != GOAL]
    summary,bands,all_ratios = [],[],{}
    for name, h in HEURISTICS.items():
        inad,incons,ratios = check(h,table)
        mean = sum(ratios.values()) / len(ratios)
        summary.append((name,inad,incons,round(mean,4)))
        all_ratios[name] = ratios
        by_band = {}
        for s, r in ratios.items():
            by_band.setdefault(band_of(table[s]),[]).append(r)
        for low, high in BANDS:
            vals = by_band[f"{low}-{high}"]
            bands.append((name,f"{low}-{high}",len(vals),round(sum(vals)/len(vals),4)))
        print(f"{name:16s} inadmissible={inad}  inconsistent={incons}  mean h/h*={mean:.4f}")

    with open("heuristic_checks.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["heuristic","inadmissible_states","inconsistent_edges","mean_h_over_hstar"])
        w.writerows(summary)

    with open("heuristic_bands.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["heuristic","depth_band","n_states","mean_h_over_hstar"])
        w.writerows(bands)

    names = list(HEURISTICS)
    with gzip.open("heuristic_ratios.csv.gz", "wt",newline="") as f:
        w = csv.writer(f)
        w.writerow(["depth"] + names)
        for s in states:
            w.writerow([table[s]] + [f"{all_ratios[n][s]:.4f}" for n in names])

    print("Mean h/h* by depth band:")
    for name,band,n,m in bands:
        print(f"  {name:16s} {band:6s} {m:.3f}")
    print("wrote heuristic_checks.csv, heuristic_bands.csv, heuristic_ratios.csv.gz")

if __name__ == "__main__":
    main()

