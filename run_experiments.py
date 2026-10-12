"""Run every agent on the fixed 38-state benchmark and write results.csv and summary.csv."""

import argparse
import csv
import random
import statistics
import pandas as pd
from heuristics import HEURISTICS
from oracle import HANDOUT,load_true_distance
from puzzle import GOAL,successors
from search import solve

SEED = 42
DEPTHS = [4,8,12,16,20,24,28]
PER_DEPTH = 5
WEIGHTS = [0, 0.5, 1, 1.5, 2, 3, 5, "greedy"]
REPEATS = 3

FIELDS = ["state_id","depth", "heuristic", "W", "moves", "expanded", "generated",
          "max_frontier", "max_stored", "seconds", "optimal", "cost_ratio", "b_star"]

def state_str(s):
    return "".join(map(str,s))

def pick_states(table):
    #The fixed benchmark set: list of (state_id,depth,state)
    rng = random.Random(SEED)
    by_depth = {}
    for s, d in table.items():
        by_depth.setdefault(d,[]).append(s)
    for d in by_depth:
        by_depth[d].sort()# dict order is BFS order; sort so sampling depends only on the seed
    chosen = []
    for d in DEPTHS:
        chosen += [(d, s) for s in rng.sample(by_depth[d], PER_DEPTH)]
    chosen += [(31, s) for s in by_depth[31]]
    chosen.append((table[HANDOUT], HANDOUT))
    return [(i,d,s) for i,(d,s) in enumerate(chosen)]

def effective_branching_factor(N, d):
    #b such that 1 + b + b^2 + ... + b^d = N + 1, found by 60 bisection steps
    if d <= 0 or N <= 0:
        return float("nan")
    lo,hi = 1.0,float(max(N,1))
    for h in range(60):
        mid = (lo +hi) / 2
        if sum(mid ** i for i in range(d+1)) <N + 1:
            lo = mid
        else:
            hi = mid
    return lo

def valid_path(path, start, moves):
    return (path[0] == start and path[-1] == GOAL
            and all(b in set(successors(a)) for a,b in zip(path,path[1:]))
            and len(path)-1 == moves)
def agents():
    yield "uninformed", "0", "manhattan", 0, False
    for h in HEURISTICS:
        for W in WEIGHTS[1:]:
            if W == "greedy":
                yield h,"greedy", h,0,True
            else:
                yield h,str(W), h,W,False

def run_one(state,h_name,W,greedy):
    #Run solve() REPEATS times; return the last result with the median time.
    times = []
    for k in range(REPEATS):
        r = solve(state,h_name,W,greedy=greedy)
        times.append(r["seconds"])
    r["seconds"] = statistics.median(times)
    return r

def run_grid(states, verbose=True):
    rows, paths = [],[]
    for sid,d,s in states:
        for h_label, w_label, h_name, W, greedy in agents():
            r = run_one(s,h_name,W,greedy)
            if "error" in r:
                raise RuntimeError(f"state {sid} {h_label} W={w_label}: {r['error']}")
            if not valid_path(r["path"], s, r["moves"]):
                raise RuntimeError(f"state {sid} {h_label} W={w_label}: invalid path")
            
            rows.append({"state_id": sid, "depth": d, "heuristic": h_label, "W": w_label,
                "moves": r["moves"], "expanded": r["expanded"], "generated": r["generated"],
                "max_frontier": r["max_frontier"], "max_stored": r["max_stored"],
                "seconds": round(r["seconds"], 6),"optimal": r["moves"] == d,"cost_ratio": round(r["moves"] / d, 4),
                "b_star": round(effective_branching_factor(r["generated"], d), 4)})
            
            if s == HANDOUT and (w_label, h_label) in {("1", "linear_conflict"),
                                                       ("greedy", "linear_conflict")}:
                agent = "A* (W=1)" if w_label == "1" else "greedy"
                for k,p in enumerate(r["path"]):
                    paths.append({"agent": agent, "heuristic": h_label, "step": k,"state": state_str(p), "moves": r["moves"],"generated": r["generated"]})
        if verbose:
            print(f"state {sid:2d} (depth {d:2d}) ")
    return rows,paths


def integration_test(table):
    by_depth = {}
    for s, d in table.items():
        by_depth.setdefault(d, []).append(s)
    easy = sorted(by_depth[8])[0]
    hard = sorted(by_depth[31])[0]
    states = [(0, 8, easy), (1, table[HANDOUT], HANDOUT), (2, 31, hard)]
    rows, paths = run_grid(states, verbose=False)     # run_grid already asserts valid paths
    df = pd.DataFrame(rows)
    ok = True

    low = df[df.W.isin(["0", "0.5", "1"])]
    c1 = bool(low.optimal.all())
    print(f"[{'PASS' if c1 else 'FAIL'}] every run with W <= 1 is optimal")

    # W = 0 with each heuristic name passed: identical node counts?
    c2 = all(len({solve(s, h, 0)["expanded"] for h in HEURISTICS}) == 1 for _, _, s in states)
    print(f"[{'PASS' if c2 else 'FAIL'}] W = 0 node count is the same for every heuristic name")

    a = df[df.W == "1"].pivot(index="state_id", columns="heuristic", values="expanded")
    # Dominance guarantees "never more nodes"; on easy states the counts can tie.
    c3 = bool(((a.misplaced >= a.manhattan) & (a.manhattan >= a.linear_conflict)).all())
    strict = int(((a.misplaced > a.manhattan) & (a.manhattan > a.linear_conflict)).sum())
    print(f"[{'PASS' if c3 else 'FAIL'}] at W = 1 expanded: misplaced >= manhattan >= linear_conflict "
          f"(strict on {strict} of {len(a)} states)")
    print(a.to_string())

    print("[PASS] every path starts at the start state, ends at the goal, uses legal moves")
    ok = c1 and c2 and c3
    print("integration test", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quick", action="store_true", help="quick integration test on 3 states only")
    args = ap.parse_args()

    table = load_true_distance()
    if args.quick:
        raise SystemExit(0 if integration_test(table) else 1)
    states = pick_states(table)
    with open("benchmark_states.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["state_id","depth","state"])
        for sid, d, s in states:
            w.writerow([sid, d, state_str(s)])
    print(f"{len(states)} benchmark states is saved in a csv")

    rows, paths = run_grid(states)
    df = pd.DataFrame(rows,columns=FIELDS)
    df.to_csv("results.csv",index=False)
    pd.DataFrame(paths).to_csv("handout_paths.csv",index=False)

    metrics = ["moves","expanded","generated","max_frontier","max_stored","seconds","optimal","cost_ratio","b_star"]
    summary = df.groupby(["heuristic","W","depth"], sort=True)[metrics].mean().reset_index()
    summary.to_csv("summary.csv", index=False, float_format="%.4f")
    print(f"non-optimal runs: {(~df.optimal).sum()}  (all with W > 1 or greedy: "
          f"{bool(df[~df.optimal].W.isin(['1.5','2','3','5','greedy']).all())})")

if __name__ == "__main__":
    main()
