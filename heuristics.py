#Every heuristic takes a state and returns an int
#lower bound on the number of moves to the goal.All are registered in the
#HEURISTICS dict.

#Also:
#misplaced(s) <= manhattan(s) <= linear_conflict(s) <= h*(s)


from puzzle import GOAL
GOAL_POS = [0]*9 #basically final state 
for cell, tile in enumerate(GOAL):
    GOAL_POS[tile] = cell
GOAL_POS = tuple(GOAL_POS)

DIST = tuple(tuple(abs(a//3 - b//3) + abs(a%3 - b%3) for b in range(9))
             for a in range(9)) #Manhattan distance

def misplaced(s):
    #Count of tiles not in their goal cell
    return sum(1 for i,t in enumerate(s) if t != 0 and i != GOAL_POS[t])

def manhattan(s):
    #Sum over tiles of grid distance to the goal cell
    return sum(DIST[i][GOAL_POS[t]] for i, t in enumerate(s) if t != 0)

def lis(seq):
    #Length of the longest strictly increasing subsequence of seq
    if not seq:
        return 0
    best = [1] * len(seq)
    for i in range(len(seq)):
        for j in range(i):
            if seq[j] < seq[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
    return max(best)

def line_extra(seq):
    #Fewest tiles that must leave a line so the remaining ones are already in order
    return len(seq) - lis(seq)

def linear_conflict(s):
    #for each row and column,2×(tiles in their goal line−longest increasing subsequence).
    total = manhattan(s)
    for r in range(3):
        seq = [GOAL_POS[t] % 3 for c in range(3)
               for t in (s[r*3+c],)
               if t != 0 and GOAL_POS[t] // 3 == r]
        total += 2 * line_extra(seq)
    for c in range(3):
        seq = [GOAL_POS[t] // 3 for r in range(3)
               for t in (s[r* 3+c],)
               if t != 0 and GOAL_POS[t] % 3 == c]
        total += 2 * line_extra(seq)
    return total

HEURISTICS = {"misplaced": misplaced,"manhattan": manhattan,"linear_conflict": linear_conflict}

if __name__ == "__main__":
    handout = (7, 2, 4, 5, 0, 6, 8, 3, 1)
    assert misplaced(handout) == 8, misplaced(handout)
    assert manhattan(handout) == 18, manhattan(handout)
    assert linear_conflict(GOAL) == 0
    assert linear_conflict(handout) == 18, linear_conflict(handout)
    b = (2, 1, 0, 3, 4, 5, 6, 7, 8)
    assert manhattan(b) == 2 and linear_conflict(b) == 4, (manhattan(b), linear_conflict(b))
    assert lis([3, 2, 1]) == 1 and line_extra([3, 2, 1]) == 2