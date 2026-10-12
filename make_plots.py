import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = "figures"
COL_W = 3.4        
HEURS = ["misplaced", "manhattan", "linear_conflict"]
LABEL = {"uninformed": "Uninformed (W = 0)", "misplaced": "Misplaced tiles","manhattan": "Manhattan", "linear_conflict": "Manhattan + linear conflict"}
COLOR = {"misplaced": "#2a78d6", "manhattan": "#eb6834","linear_conflict": "#1baf7a", "uninformed": "#7a7a7a"}
MARKER = {"misplaced": "o", "manhattan": "s", "linear_conflict": "^", "uninformed": "D"}
W_ORDER = ["0.5", "1", "1.5", "2", "3", "5", "greedy"]
W_X = {w: i for i, w in enumerate(W_ORDER)}      
plt.rcParams.update({"font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "legend.fontsize": 6.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "lines.linewidth": 1.5, "lines.markersize": 4,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e3e3e3", "grid.linewidth": 0.5, "axes.edgecolor": "#888888","legend.frameon": False, "savefig.bbox": "tight", "pdf.fonttype": 42,})

def save(fig, name, caption):
    fig.savefig(os.path.join(OUT, name + ".pdf"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=200)
    plt.close(fig)
    print(f"{name}: {caption}")

def line(ax, x, y, key, **kw):
    ax.plot(x, y, color=COLOR[key], marker=MARKER[key], label=LABEL[key], **kw)

def fig_vs_depth(df, metric, name, ylabel, caption):
    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    base = df[df.heuristic == "uninformed"].groupby("depth")[metric].mean()
    line(ax, base.index, base.values, "uninformed", linestyle="--")
    for h in HEURS:
        s = df[(df.heuristic == h) & (df.W == "1")].groupby("depth")[metric].mean()
        line(ax, s.index, s.values, h)
    ax.set_yscale("log")
    ax.set_xlabel("Optimal solution depth d (moves)")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(df.depth.unique()))
    ax.legend(loc="upper left")
    save(fig, name, caption)

def fig2(df):
    hard = df[df.depth >= 24]
    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    for h in HEURS:
        s = hard[hard.heuristic == h].groupby("W")["generated"].mean().reindex(W_ORDER)
        line(ax, range(len(W_ORDER)), s.values, h)
    base = hard[hard.heuristic == "uninformed"].generated.mean()
    ax.axhline(base, color=COLOR["uninformed"], linestyle="--", linewidth=1,label=LABEL["uninformed"])
    ax.set_yscale("log")
    ax.set_xticks(range(len(W_ORDER)), W_ORDER)
    ax.set_xlabel("Weight W in f = g + W·h")
    ax.set_ylabel("Mean nodes generated (log scale)")
    ax.legend(loc="lower left")
    save(fig, "fig2_nodes_vs_weight","Mean nodes generated against W on the 15 states with depth >= 24.")

def fig3(df):
    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    xs = range(len(W_ORDER))
    numeric = [float(w) for w in W_ORDER[:-1]]
    ax.plot(range(1, len(numeric)), numeric[1:], color="#555555", linestyle=":", linewidth=1,label="y = W (weighted A* bound)")
    ax.axhline(1, color="#555555", linewidth=0.8)
    for h in HEURS:
        s = df[df.heuristic == h].groupby("W")["cost_ratio"].mean().reindex(W_ORDER)
        line(ax, xs, s.values, h)
        if s["greedy"] > 5.3:                       # off the top: label the value instead
            ax.annotate(f"{LABEL[h]}: {s['greedy']:.1f}", (len(W_ORDER) - 1, 5.3),
                        xytext=(-4, -2),textcoords="offset points", ha="right", va="top",fontsize=6, color="#333333")
    ax.set_xticks(list(xs), W_ORDER)
    ax.set_ylim(0.9, 5.3)
    ax.set_xlabel("Weight W in f = g + W·h")
    ax.set_ylabel("Mean solution length / optimal")
    ax.legend(loc="upper left")
    save(fig, "fig3_cost_ratio_vs_weight","Mean cost ratio against W over all 38 states; greedy has no bound.")

def fig4(df):
    hard = df[df.depth >= 28]
    fig, ax = plt.subplots(figsize=(COL_W, 2.5))
    xs = range(len(W_ORDER))
    for h in HEURS:
        s = hard[hard.heuristic == h].groupby("W")["moves"].mean().reindex(W_ORDER)
        line(ax,xs,s.values,h)
    opt = hard.groupby("state_id").depth.first().mean()
    ax.axhline(opt, color="#222222", linewidth=0.9, label=f"True optimum (mean {opt:.1f})")
    ax.axhline(31, color="#555555", linestyle=":", linewidth=1, label="Upper bound: 31 moves")
    ax.set_xticks(list(xs), W_ORDER)
    ax.set_xlabel("Weight W in f = g + W·h")
    ax.set_ylabel("Mean solution length (moves)")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks([25, 30, 40, 60, 100, 200, 400])
    ax.legend(loc="upper left")
    save(fig, "fig4_length_vs_bound","Mean solution length on the 7 states of depth >= 28 against the optimum and the 31-move bound.")

def fig5():
    r = pd.read_csv("heuristic_ratios.csv.gz")
    fig,ax = plt.subplots(figsize=(COL_W, 2.4))
    bp = ax.boxplot([r[h] for h in HEURS], whis=(5, 95), showfliers=False, patch_artist=True,widths=0.5, medianprops={"color": "#222222"})
    for patch,h in zip(bp["boxes"],HEURS):
        patch.set_facecolor(COLOR[h])
        patch.set_alpha(0.75)
    for i, h in enumerate(HEURS, start=1):
        ax.plot(i, r[h].mean(), marker="x", color="#222222")
        ax.annotate(f"mean {r[h].mean():.2f}", (i, r[h].quantile(0.95)), xytext=(0, 4),textcoords="offset points", ha="center", va="bottom", fontsize=6.5)
    ax.set_xticks([1,2,3], ["Misplaced", "Manhattan", "Manhattan +\nlinear conflict"])
    ax.set_ylabel("h(s) / h*(s)")
    ax.set_ylim(0, 1.05)
    save(fig, "fig5_h_ratio_box","h/h* over all 181,439 non-goal states (whiskers 5th-95th percentile, x = mean).")

def draw_board(ax,s,fill):
    for i, ch in enumerate(s):
        r, c = divmod(i,3)
        if ch != "0":
            ax.add_patch(plt.Rectangle((c + 0.05,2-r+0.05),0.9,0.9,facecolor=fill, edgecolor="none"))
            ax.text(c + 0.5, 2 - r + 0.5, ch, ha="center", va="center",fontsize=6, color="white", fontweight="bold")
    ax.add_patch(plt.Rectangle((0, 0), 3, 3, fill=False, edgecolor="#888888", linewidth=0.6))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_aspect("equal")
    ax.axis("off")

def pick(n, k=12):
    if n <= k:
        return list(range(n))
    return sorted({round(i*(n-1)/(k-1)) for i in range(k)})

def fig7():
    p = pd.read_csv("handout_paths.csv", dtype={"state": str})
    agents = [("A* (W=1)", COLOR["linear_conflict"]), ("greedy", COLOR["manhattan"])]
    fig,axes = plt.subplots(2,12,figsize=(2*COL_W,1.6))
    for row,(agent, fill) in enumerate(agents):
        a = p[p.agent == agent].sort_values("step")
        idx = pick(len(a))
        for col in range(12):
            ax = axes[row][col]
            if col < len(idx):
                rec = a.iloc[idx[col]]
                draw_board(ax,rec.state,fill)
                ax.set_title(f"move {rec.step}", fontsize=5.5, pad=2)
            else:
                ax.axis("off")
        first = a.iloc[0]
        axes[row][0].text(-0.4,1.5,f"{agent}\n{first.moves} moves\n{first.generated} generated",ha="right", va="center", fontsize=6.5, transform=axes[row][0].transData)
    save(fig, "fig7_board_sequence","Handout state solved by A* and greedy (both with linear conflict), 12 evenly spaced boards each.")

def bstar_table(df):
    bands = pd.cut(df.depth, [0,10,20,31],labels=["1-10", "11-20", "21-31"])
    sel = df[(df.W == "1")|(df.heuristic == "uninformed")].assign(band=bands)
    t = sel.groupby(["heuristic", "band"], observed=True).b_star.mean().unstack()
    t = t.reindex(["uninformed"] + HEURS).round(3)
    t.to_csv(os.path.join(OUT,"bstar_table.csv"))
    with open(os.path.join(OUT,"bstar_table.tex"), "w") as f:
        f.write("% Effective branching factor b* at W = 1 (uninformed: W = 0), mean per depth band\n")
        f.write("\\begin{tabular}{lrrr}\n\\hline\nAgent & $d$ 1--10 & $d$ 11--20 & $d$ 21--31 \\\\\n\\hline\n")
        for h,row in t.iterrows():
            f.write(f"{LABEL[h]} & " + " & ".join(f"{v:.3f}" for v in row) + " \\\\\n")
        f.write("\\hline\n\\end{tabular}\n")
    print("b* table (W = 1):")
    print(t.to_string())

def main():
    os.makedirs(OUT,exist_ok=True)
    df = pd.read_csv("results.csv", dtype={"W": str})
    fig_vs_depth(df, "generated", "fig1_nodes_vs_depth", "Mean nodes generated (log scale)",
                 "Nodes generated against optimal depth at W = 1, with the uninformed baseline.")
    fig2(df)
    fig3(df)
    fig4(df)
    fig5()
    fig_vs_depth(df,"max_stored","fig6_space_vs_depth","Mean peak states stored (log scale)",
                 "Peak number of states held in memory against depth at W = 1.")
    fig7()
    bstar_table(df)

if __name__ == "__main__":
    main()
