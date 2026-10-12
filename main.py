import argparse
import sys
from heuristics import HEURISTICS
from puzzle import board_str, read_state
from search import solve

def non_negative_float(text):
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"weight must be a number, got {text!r}")
    if value < 0:
        raise argparse.ArgumentTypeError(f"weight must be >= 0, got {value}")
    return value

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Solve the 8-puzzle with weighted best-first search, "
                                            "f(n) = g(n) + W*h(n).")
    p.add_argument("--input", default="start.txt",
                   help="board file: 3 lines of 3 digits, 0 = blank (default: start.txt)")
    p.add_argument("--heuristic", choices=sorted(HEURISTICS), default="manhattan",
                   help="heuristic h(n) (default: manhattan)")
    p.add_argument("--weight", type=non_negative_float, default=1.0,
                   help="weight W >= 0: 0 = uninformed, 1 = A*, >1 = weighted A* (default: 1)")
    p.add_argument("--greedy", action="store_true",
                   help="greedy best-first search: rank by h alone (ignores --weight)")
    p.add_argument("--show-path", action="store_true",
                   help="print every board along the solution")
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    try:
        start = read_state(args.input)
    except FileNotFoundError:
        print(f"Error: input file {args.input!r} not found.")
        return 1
    except ValueError as e:
        print(f"Error: badly formatted input. {e}")
        return 1
    agent = "greedy best-first" if args.greedy else (
        "uninformed (W = 0)" if args.weight == 0 else
        "A* (W = 1)" if args.weight == 1 else f"weighted A* (W = {args.weight:g})")
    print("Start state:")
    print(board_str(start))
    print(f"Agent: {agent}, heuristic: {args.heuristic}")

    r = solve(start, args.heuristic, args.weight, greedy=args.greedy)
    if "error" in r:
        if r["error"] == "unsolvable":
            print("This state is unsolvable: its inversion parity differs from the goal's.")
        else:
            print("Search failed to find a solution.")
        return 2

    print(f"Moves: {r['moves']}")
    print(f"Nodes expanded: {r['expanded']}")
    print(f"Nodes generated: {r['generated']}")
    print(f"Peak frontier: {r['max_frontier']}")
    print(f"Peak stored: {r['max_stored']}")
    print(f"Time: {r['seconds']:.4f} s")
    if args.show_path:
        print("\nSolution path:")
        for k, s in enumerate(r["path"]):
            print(f"Move {k}:")
            print(board_str(s))
            print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
