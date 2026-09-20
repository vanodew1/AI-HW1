import math
import os
import random
import sys
import matplotlib.pyplot as plt

def booth(x, y): 
    return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2 
def himmelblau(x, y):
    return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2
def griewank(x, y):
    return 1 + (x ** 2 + y ** 2) / 4000 - math.cos(x) * math.cos(y / math.sqrt(2))

problem = {
    "Booth":      (booth,      (-10, 10), 0.0),
    "Himmelblau": (himmelblau, (-5, 5),   0.0),
    "Griewank":   (griewank,   (-30, 30), 0.0),
}

def clip(value, low, high): # the coordinates range 
    return max(low, min(high, value))

def simulated_annealing(func, bounds, mode="min", step=0.5, T0=1.0, T_decay=0.1, K=100, seed=None): #the main thing
    rng = random.Random(seed)
    low, high = bounds
    if mode == "min":
        sign = 1     # minimizing
    else:
        sign = -1    # maximizing
    x = rng.uniform(low, high)
    y = rng.uniform(low, high)
    f_current = func(x, y)
    best_x, best_y, best_f = x, y, f_current # the best solution found (so far) 
    xs, ys, fs, best_fs = [x], [y], [f_current], [best_f]
    n_stages = int(round(T0 / T_decay))

    for stage in range(n_stages):
        T = T0 - stage * T_decay
        for _ in range(K): #pick a random neighbour 
            new_x = clip(x + rng.uniform(-step, step), low, high)
            new_y = clip(y + rng.uniform(-step, step), low, high)
            f_new = func(new_x, new_y) # the new solution's value
            delta = sign * (f_new - f_current)
            if delta <= 0: # delta is the change
                accept = True                     
            else:
                accept = rng.random() < math.exp(-delta / T)  
            if accept:
                x, y, f_current = new_x, new_y, f_new
            if sign * (f_current - best_f) < 0:
                best_x, best_y, best_f = x, y, f_current

            xs.append(x) # appending to the search history
            ys.append(y)
            fs.append(f_current)
            best_fs.append(best_f)
    return { 
        "x": xs, "y": ys, "f": fs, "best_f_history": best_fs, "best_x": best_x, "best_y": best_y, "best_f": best_f, "final_x": x, "final_y": y, "final_f": f_current, "mode": mode,
    }

def multi_start(func, bounds, mode, n_starts, step, T0, T_decay, K, seed0=0):
    runs = [simulated_annealing(func, bounds, mode, step, T0, T_decay, K, seed=seed0 + i) for i in range(n_starts)] # basically its just running the simulated annealing multiple times and storing the results in a list
    sign = 1
    if mode == "max":
        sign = -1
    best_run = min(runs, key=lambda r: sign * r["best_f"])
    return best_run, [r["best_f"] for r in runs]


def evaluate_setting(func, bounds, true_min, step, T0, T_decay, K, runs=100, tolerance=1e-2):
    successes = 0
    total_best = 0.0
    for seed in range(runs):
        r = simulated_annealing(func, bounds, "min", step, T0, T_decay, K, seed)
        total_best += r["best_f"]
        if r["best_f"] - true_min < tolerance:
            successes += 1
    return successes / runs, total_best / runs

def tune(name, func, bounds, true_min, settings): # tunes the parameters 
    print(f"\nTuning on {name}  (100 random starts per row)")
    print(f"{'step':>5} {'T0':>5} {'decay':>6} {'K':>5} | {'success':>8} {'mean best f':>12}")
    best_row = None
    for step, T0, T_decay, K in settings:
        rate, mean_f = evaluate_setting(func, bounds, true_min, step, T0, T_decay, K)
        print(f"{step:>5} {T0:>5} {T_decay:>6} {K:>5} | {rate:>7.0%} {mean_f:>12.4f}")
        if best_row is None or (rate, -mean_f) > (best_row[0], -best_row[1]):
            best_row = (rate, mean_f, (step, T0, T_decay, K))
    return best_row[2]

# Part b

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")

# x, y and f each get their own panel, so the only pair sharing an axis is
# f against best-f-so-far, and those two are kept far apart in hue
COLOUR_X     = "#2a78d6"   # blue
COLOUR_Y     = "#eb6834"   # orange
COLOUR_F     = "#4a3aa7"   # violet
COLOUR_BEST  = "#e34948"   # red
COLOUR_GRID  = "#d9d8d4"
COLOUR_STAGE = "#ebeae6"
COLOUR_TEXT  = "#52514e"

def style_axis(ax, ylabel): # keeps the grid and axes faint so the data stands out
    ax.set_ylabel(ylabel, color=COLOUR_TEXT)
    ax.grid(True, axis="y", color=COLOUR_GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOUR_GRID)
    ax.spines["bottom"].set_color(COLOUR_GRID)
    ax.tick_params(colors=COLOUR_TEXT, labelsize=9)

def mark_temperature_drops(ax, n_stages, K): # a faint line every time T steps down
    for stage in range(1, n_stages):
        ax.axvline(stage * K, color=COLOUR_STAGE, linewidth=1.0)

def plot_run(result, name, params, filename, show=False): # one figure for one run
    step, T0, T_decay, K = params
    xs, ys, fs = result["x"], result["y"], result["f"]
    best_fs = result["best_f_history"]
    iterations = list(range(len(xs)))
    n_stages = int(round(T0 / T_decay))

    fig, (ax_x, ax_y, ax_f) = plt.subplots(3, 1, figsize=(9, 8.5), sharex=True)

    for ax, values, label, colour, best in ( # the x and y panels
        (ax_x, xs, "x", COLOUR_X, result["best_x"]),
        (ax_y, ys, "y", COLOUR_Y, result["best_y"]),
    ):
        mark_temperature_drops(ax, n_stages, K)
        ax.plot(iterations, values, color=colour, linewidth=0.9)
        ax.axhline(best, color=colour, linewidth=1.0, linestyle="--", alpha=0.55)
        style_axis(ax, label)

    mark_temperature_drops(ax_f, n_stages, K) # the f panel
    ax_f.plot(iterations, fs, color=COLOUR_F, linewidth=0.9, label="f at current point")
    ax_f.plot(iterations, best_fs, color=COLOUR_BEST, linewidth=1.8, label="best f so far")
    style_axis(ax_f, "f(x, y)")
    ax_f.set_xlabel("iteration", color=COLOUR_TEXT)

    positive = [v for v in fs if v > 0] # f drops by orders of magnitude, so a
    if positive and max(positive) / min(positive) > 100: # linear axis hides the
        ax_f.set_yscale("log")                           # late convergence
        ax_f.set_ylabel("f(x, y)   (log scale)", color=COLOUR_TEXT)

    ax_f.legend(loc="upper right", frameon=False, fontsize=9)

    fig.suptitle(f"Simulated annealing on the {name} function\n" f"step={step}, T0={T0}, decay={T_decay}, K={K}   |   " f"best f = {result['best_f']:.6f} at ({result['best_x']:.4f}, {result['best_y']:.4f})", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fig.savefig(filename, dpi=150)
    print(f"  saved {filename}")

    if show:
        plt.show()
    else:
        plt.close(fig)

def make_plots(tuned=None, show=False): # one figure per function, before and after tuning
    print("\n" + "=" * 66)
    print("PLOTS: x, y and f over iterations")
    print("=" * 66)
    starting = (0.5, 1.0, 0.1, 100)
    for name, (func, bounds, true_min) in problem.items():
        r = simulated_annealing(func, bounds, "min", *starting, seed=1)
        plot_run(r, name, starting, os.path.join(PLOT_DIR, f"{name.lower()}_starting.png"), show)
        if tuned is not None:
            params = tuned[name]
            r = simulated_annealing(func, bounds, "min", *params, seed=1)
            plot_run(r, name, params, os.path.join(PLOT_DIR, f"{name.lower()}_tuned.png"), show)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "plots": # redraw without re-tuning
        make_plots(show="--show" in sys.argv)
        return

    print("=" * 66)
    print("STEP 1: starting parameters (step=0.5, T0=1, decay=0.1, K=100)")
    print("=" * 66)
    for name, (func, bounds, true_min) in problem.items():
        r = simulated_annealing(func, bounds, "min", 0.5, 1.0, 0.1, 100, seed=1)
        print(f"{name:<11} min found: f={r['best_f']:.5f} at " f"(x={r['best_x']:.4f}, y={r['best_y']:.4f})")
    settings = [
        (0.5, 1.0, 0.1, 100),    # starting values
        (0.5, 1.0, 0.1, 500),    # longer run
        (1.0, 1.0, 0.1, 500),    # larger neighbourhood
        (0.5, 5.0, 0.5, 500),    # hot start
        (1.0, 1.0, 0.1, 1000),   # longer stay 
        (0.5, 1.0, 0.1, 1000),   
    ]
    tuned = {}
    for name, (func, bounds, true_min) in problem.items():
        tuned[name] = tune(name, func, bounds, true_min, settings)
    print("\n" + "=" * 66)
    print("STEP 3: tuned parameters, 20 random restarts, minimum AND maximum")
    print("=" * 66)
    n_starts = 20
    for name, (func, bounds, true_min) in problem.items():
        step, T0, T_decay, K = tuned[name]
        print(f"\n{name}  (tuned: step={step}, T0={T0}, decay={T_decay}, K={K})")
        for mode in ("min", "max"):
            best, all_best = multi_start(func, bounds, mode, n_starts, step, T0, T_decay, K)    
            agree = sum(abs(v - best["best_f"]) < 1e-2 for v in all_best)
            print(f"  {mode}: f={best['best_f']:.5f} at " f"(x={best['best_x']:.4f}, y={best['best_y']:.4f})  "f"[{agree}/{n_starts} restarts reached it]")

    make_plots(tuned, show="--show" in sys.argv)
if __name__ == "__main__":
    main()