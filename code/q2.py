import math
import random

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

def main():
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

if __name__ == "__main__":
    main()