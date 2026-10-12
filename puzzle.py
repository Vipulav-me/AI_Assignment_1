"""
Cell i of a state sits at row i // 3, column i % 3:

    0 1 2
    3 4 5
    6 7 8
"""
GOAL = (0,1,2,3,4,5,6,7,8)
def _neighbours(i):
    #Cells one step up, down, left or right of cell i.
    r,c = divmod(i,3)
    out = []
    if r > 0:
        out.append(i-3)#up 
    if r < 2:
        out.append(i+3)# down
    if c > 0:
        out.append(i-1)# left
    if c < 2:
        out.append(i+1)# right
    return tuple(out)

# NEIGHBOURS[i]: the cells the blank can move to when it sits in cell i.
NEIGHBOURS = tuple(_neighbours(i) for i in range(9))

def successors(s):
    #This func yields every state reachable from s in one move 
    z = s.index(0)
    for j in NEIGHBOURS[z]:
        t = list(s)
        t[z],t[j] = t[j],t[z]
        yield tuple(t)

def inversions(s):
    #Number of pairs of tiles (blank ignored) that appear in the wrong relative order
    tiles = [t for t in s if t != 0]
    return sum(1 for i in range(len(tiles))
               for j in range(i+1,len(tiles))
               if tiles[i] > tiles[j])

def solvable(s): ###### Parity is the same 
    #True if s can reach GOAL.
    return inversions(s) % 2 == inversions(GOAL) % 2

def read_state(path):
    with open(path) as f:
        text = f.read()
    tokens = text.split()
    if len(tokens) != 9:
        tokens = [ch for ch in text if not ch.isspace()]
    try:
        values = tuple(int(t) for t in tokens)
    except ValueError:
        raise ValueError(f"{path}: every entry must be a digit 0-8, got {tokens}")
    if len(values) != 9 or sorted(values) != list(range(9)):
        raise ValueError(f"{path}: expected the digits 0-8 exactly once in a 3x3 grid, "
                         f"got {list(values)}")
    return values

def board_str(s):
    #Three-line picture of the board, blank shown as '_'.
    cells = ["_" if t == 0 else str(t) for t in s]
    return "\n".join(" ".join(cells[r*3:r*3+3]) for r in range(3))

if __name__ == "__main__":
    handout = (7,2,4,5,0,6,8,3,1)
    swapped = (0,2,1,3,4,5,6,7,8)   
    assert solvable(handout), "handout state should be solvable"
    assert not solvable(swapped), "goal with 1 and 2 swapped should be unsolvable"
    assert sorted(successors(GOAL)) == [(1, 0, 2, 3, 4, 5, 6, 7, 8),
                                        (3, 1, 2, 0, 4, 5, 6, 7, 8)]
    print(board_str(handout))
