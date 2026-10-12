# 8-puzzle A1: weighted best-first search

This project solves the 8-puzzle with one weighted best-first search,
`f(n) = g(n) + W·h(n)`. The same search runs every agent: uninformed (W = 0),
A* (W = 1), weighted A* (W > 1) and greedy best-first. It comes with three
admissible heuristics (misplaced tiles, Manhattan distance, and Manhattan +
linear conflict). Partner B's scripts check the solver against exact BFS
distances for all 181,440 solvable states and benchmark every agent.

## Requirements

* Python 3.10 or newer (tested with 3.12.3)
* `pandas` and `matplotlib`, used only by `run_experiments.py` and `make_plots.py`.
  The solver (`main.py`) uses only the standard library.

```
pip install pandas matplotlib
```

## Input file format

Three lines of three digits, 0 to 8, each used exactly once, with 0 for the blank.
Digits may be separated by spaces. `start.txt` holds the handout state:

```
7 2 4
5 0 6
8 3 1
```

The goal is `0 1 2 / 3 4 5 / 6 7 8` (blank top-left).

## Running the solver

```
python main.py [--input FILE] [--heuristic {misplaced,manhattan,linear_conflict}]
               [--weight W] [--greedy] [--show-path]
```

| Option | Meaning |
|---|---|
| `--input` | board file (default `start.txt`) |
| `--heuristic` | heuristic h(n) (default `manhattan`) |
| `--weight` | W ≥ 0: 0 = uninformed, 1 = A*, > 1 = weighted A* (default 1) |
| `--greedy` | rank nodes by h alone (`--weight` is then ignored) |
| `--show-path` | print every board along the solution |

The program prints a clear message instead of a traceback when the state is
unsolvable, the file is missing or badly formatted, or W is negative.

### The four example commands and their output

Running times depend on the machine.

```
$ python main.py --input start.txt --heuristic manhattan --weight 0
Start state:
7 2 4
5 _ 6
8 3 1
Agent: uninformed (W = 0), heuristic: manhattan
Moves:           26
Nodes expanded:  171711
Nodes generated: 458204
Peak frontier:   24983
Peak stored:     177809
Time:            0.5964 s

$ python main.py --input start.txt --heuristic linear_conflict --weight 1 --show-path
Start state:
7 2 4
5 _ 6
8 3 1
Agent: A* (W = 1), heuristic: linear_conflict
Moves:26
Nodes expanded:  862
Nodes generated: 2295
Peak frontier:   519
Peak stored:     1356
Time: 0.0100 s

Solution path:
Move 0:
7 2 4
5 _ 6
8 3 1

Move 1:
7 2 4
_ 5 6
8 3 1

Move 2:
_ 2 4
7 5 6
8 3 1

...   (moves 3-25 omitted here; the program prints all of them)

Move 26:
_ 1 2
3 4 5
6 7 8


$ python main.py --input start.txt --heuristic manhattan --weight 2
Start state:
7 2 4
5 _ 6
8 3 1
Agent: weighted A* (W = 2), heuristic: manhattan
Moves:30
Nodes expanded:  251
Nodes generated: 677
Peak frontier:   170
Peak stored:     409
Time: 0.0008 s

$ python main.py --input start.txt --heuristic manhattan --greedy
Start state:
7 2 4
5 _ 6
8 3 1
Agent: greedy best-first, heuristic: manhattan
Moves:88
Nodes expanded:  292
Nodes generated: 794
Peak frontier:   180
Peak stored:     326
Time: 0.0009 s
```

## Reproducing all results

Run these in order from this folder:

```
python oracle.py              
python check_heuristics.py    
python run_experiments.py    
python make_plots.py         
```


## Files

| File | What it does 
|---|---
| `puzzle.py` | Board model: GOAL, NEIGHBOURS, `successors`, parity check, `read_state`, `board_str`. Holds the agreed interface. 
| `search.py` | `solve()`: weighted best-first search with stale-entry skipping, reopening, and the deeper-node tie-break. Also `reconstruct()` and `measure_tiebreak()`
| `heuristics.py` | `misplaced`, `manhattan`, `linear_conflict` and the `HEURISTICS` dict 
| `main.py` | Command-line front end (argparse) 
| `oracle.py` | BFS from the goal that gives the exact distance h* of all 181,440 states; cached in `true_distance.pkl`  
| `check_heuristics.py` | Checks admissibility and consistency on every state, and computes mean h/h*  
| `run_experiments.py` | Fixed 38-state benchmark × every agent (836 runs), median-of-3 timing, path validation;
| `make_plots.py` | Figures 1–7 and the b* table from the CSV files 
| `start.txt` | The handout start state 
| `figures/` | Output of `make_plots.py` 
| `report.pdf` | The report 

