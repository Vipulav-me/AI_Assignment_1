
#One function covers every agent. With unit move costs,g(n) is the number of
#moves so far and nodes are ranked by
#    f(n) = g(n) + W * h(n)
import heapq
import itertools
import time
from heuristics import HEURISTICS
from puzzle import GOAL,solvable,successors

TIE_SIGN = -1
def reconstruct(parent,s):
    #Follow parent pointers from s back to the start and return the path start -> s.
    path = []
    while s is not None:
        path.append(s)
        s = parent[s]
    path.reverse()
    return path

def solve(start,h_name,W,greedy=False):
    #Search from start to GOAL and return a result dict.
    #h_name : key of HEURISTICS ("misplaced", "manhattan", "linear_conflict")
    #greedy : if True, rank nodes by h alone

    #So this func returns
    #dict {path (list of states from start to GOAL (inclusive)),moves,expanded,generated (successor states produced by expansions),
    #      max_frontier (peak number of entries in the priority queue),max_stored ,seconds).
    if not solvable(start):
        return {"error": "unsolvable"}
    h = HEURISTICS[h_name]
    W = float(W)
    if greedy:
        def rank(g,s):
            return (h(s),TIE_SIGN*g)
    elif W == 0:
        # Skip the heuristic call entirely: W*h = 0 for every heuristic.
        def rank(g,s):
            return (g,TIE_SIGN*g)
    else:
        def rank(g,s):
            return (g+W *h(s),TIE_SIGN*g)

    t0 = time.perf_counter()
    counter = itertools.count()
    g_best = {start: 0}
    parent = {start: None}
    heap = [(rank(0,start),next(counter),start,0)]
    expanded = 0
    generated = 0
    max_frontier = 1
    max_stored = 1
    while heap:
        i,j,s,g = heapq.heappop(heap)
        if g > g_best[s]:
            continue                 
        if s == GOAL:
            path = reconstruct(parent,s)
            return {"path": path,"moves": len(path)-1,"expanded": expanded,"generated": generated,"max_frontier": max_frontier,
                    "max_stored": max_stored,"seconds": time.perf_counter()-t0}
        expanded += 1
        g2 = g + 1
        for s2 in successors(s):
            generated += 1
            if s2 not in g_best or g2 < g_best[s2]:
                g_best[s2] = g2
                parent[s2] = s
                heapq.heappush(heap,(rank(g2, s2),next(counter),s2,g2))
        if len(heap) > max_frontier:
            max_frontier = len(heap)
        max_stored = len(g_best)
    return {"error":"failure"}


def measure_tiebreak(start=(7,2,4,5,0,6,8,3,1),h_name="manhattan"):
    global TIE_SIGN
    out = {}
    for sign,label in ((-1,"-g (prefer deeper)"),(+1, "+g (prefer shallower)")):
        TIE_SIGN = sign
        r = solve(start,h_name,1)
        out[label] = (r["moves"],r["expanded"])
    TIE_SIGN = -1
    return out

if __name__ == "__main__":
    handout = (7,2,4,5,0,6,8,3,1)
    r0 = solve(handout, "manhattan",0)
    r1 = solve(handout, "manhattan",1)
    assert r0["moves"] == 26 and r1["moves"] == 26, (r0["moves"], r1["moves"])
    assert r1["expanded"] < r0["expanded"]
    print(f"W=0: {r0['moves']} moves, {r0['expanded']} expanded")
    print(f"W=1 manhattan: {r1['moves']} moves, {r1['expanded']} expanded")
    for label,(moves, exp) in measure_tiebreak().items():
        print(f"tie-break {label}: {moves} moves, {exp} expanded")
