
"""Moves are reversible, so the BFS distance FROM the goal to a state equals the
#fewest moves TO the goal from that state.  One BFS therefore gives the exact
#optimal cost h*(s) of every solvable state. 
"""
import os
import pickle
from collections import Counter,deque
from puzzle import GOAL,successors

PKL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "true_distance.pkl")
HANDOUT = (7,2,4,5,0,6,8,3,1)

def build_true_distance():
    #BFS outward from GOAL; returns {state: fewest moves to GOAL}.
    true_distance = {GOAL: 0}
    queue = deque([GOAL])
    while queue:
        s = queue.popleft()
        d = true_distance[s]+ 1
        for s2 in successors(s):
            if s2 not in true_distance:
                true_distance[s2] = d
                queue.append(s2)
    return true_distance

def load_true_distance():
    if os.path.exists(PKL):
        with open(PKL,"rb") as f:
            return pickle.load(f)
    table = build_true_distance()
    with open(PKL,"wb") as f:
        pickle.dump(table, f, protocol=pickle.HIGHEST_PROTOCOL)
    return table

def depth_histogram(table):
    return dict(sorted(Counter(table.values()).items()))

if __name__ == "__main__":
    table = load_true_distance()
    hist = depth_histogram(table)
    print(f"Reachable states: {len(table)}")
    print(f"Maximum depth: {max(hist)}")
    print(f"Handout state 7 2 4 / 5 0 6 / 8 3 1 has distance {table[HANDOUT]}")
    print("States per depth:")
    for d,n in hist.items():
        print(f"  {d:2d}: {n}")
    assert len(table) == 181440, "expected 181,440 reachable states"
    assert max(hist) == 31, "expected maximum depth 31"
    assert table[HANDOUT] == 26, "expected handout state at depth 26"
