#!/usr/bin/env python3
"""
Unified experimental driver for convex hull filtering study.

Compares:
- Relaxed streaming filter
- Akl–Toussaint heuristic

Measures:
- Reduction ratio
- Filter time
- Hull time
- Total pipeline time

Outputs:
- CSV file for statistical analysis and plotting
"""

import csv
import time
import random
import math
from typing import List, Tuple
import gc
gc.disable()

from relaxed_filter import RelaxedHullFilter, convex_hull, akl_toussaint_filter
# from akl_filter import akl_toussaint_filter  # place your Akl code here

Point = Tuple[float, float]

# ------------------------------------------------------------
# Geometry generators
# ------------------------------------------------------------

def gen_uniform_square(n: int, seed=None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]


def gen_uniform_disk(n: int, seed=None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    pts = []
    for _ in range(n):
        r = math.sqrt(random.random())
        theta = 2 * math.pi * random.random()
        pts.append((r * math.cos(theta), r * math.sin(theta)))
    return pts


def gen_superellipse(n: int, m=4, seed=None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    pts = []
    for _ in range(n):
        theta = 2 * math.pi * random.random()
        r = (abs(math.cos(theta))**m + abs(math.sin(theta))**m) ** (-1/m)
        pts.append((r * math.cos(theta), r * math.sin(theta)))
    return pts


def gen_gaussian(n: int, seed=None) -> List[Point]:
    if seed is not None:
        random.seed(seed)
    return [(random.gauss(0, 1), random.gauss(0, 1)) for _ in range(n)]


GEOMETRIES = {
    "square": gen_uniform_square,
    "disk": gen_uniform_disk,
    "superellipse": gen_superellipse,
    "gaussian": gen_gaussian,
}

# ------------------------------------------------------------
# Timing utility
# ------------------------------------------------------------

def timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed

# ------------------------------------------------------------
# Single trial
# ------------------------------------------------------------

def run_trial(points: List[Point], s=1):
    n = len(points)

    # -------------------------
    # Relaxed filter
    # -------------------------
    filt = RelaxedHullFilter(s=s)

    start = time.perf_counter()
    for p in points:
        filt.add(p)
    filt.finalize()
    filter_time_relaxed = time.perf_counter() - start

    R_relaxed = filt.candidate_set()

    hull_relaxed, hull_time_relaxed = timed(convex_hull, R_relaxed)

    total_relaxed = filter_time_relaxed + hull_time_relaxed

    # -------------------------
    # Akl filter
    # -------------------------
    R_akl, filter_time_akl = timed(akl_toussaint_filter, points)
    hull_akl, hull_time_akl = timed(convex_hull, R_akl)

    total_akl = filter_time_akl + hull_time_akl

    # -------------------------
    # Baseline hull only
    # -------------------------
    hull_full, hull_time_full = timed(convex_hull, points)

    # -------------------------
    # Verify correctness
    # -------------------------
    assert sorted(hull_relaxed) == sorted(hull_full)
    assert sorted(hull_akl) == sorted(hull_full)

    return {
        "n": n,
        "relaxed_kept": len(R_relaxed),
        "akl_kept": len(R_akl),
        "relaxed_ratio": len(R_relaxed) / n,
        "akl_ratio": len(R_akl) / n,
        "filter_time_relaxed": filter_time_relaxed,
        "hull_time_relaxed": hull_time_relaxed,
        "total_time_relaxed": total_relaxed,
        "filter_time_akl": filter_time_akl,
        "hull_time_akl": hull_time_akl,
        "total_time_akl": total_akl,
        "hull_time_full": hull_time_full,
    }

# ------------------------------------------------------------
# Main experiment loop
# ------------------------------------------------------------

def run_experiments(
    output_csv="results.csv",
    ns = (10_000, 50_000, 100_000, 500_000, 1_000_000),
    trials=20,
    s_values=(1,)
):

    fieldnames = [
        "geometry",
        "n",
        "trial",
        "s",
        "relaxed_kept",
        "akl_kept",
        "relaxed_ratio",
        "akl_ratio",
        "filter_time_relaxed",
        "hull_time_relaxed",
        "total_time_relaxed",
        "filter_time_akl",
        "hull_time_akl",
        "total_time_akl",
        "hull_time_full",
    ]

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # for geom_name, generator in GEOMETRIES.items():
        #     for n in ns:
        #         for trial in range(trials):
        #             points = generator(n, seed=trial)

        #             for s in s_values:
        #                 result = run_trial(points, s=s)
        #                 row = {
        #                     "geometry": geom_name,
        #                     "trial": trial,
        #                     "s": s,
        #                     **result,
        #                 }
        #                 writer.writerow(row)

        #                 print(f"{geom_name}, n={n}, trial={trial}, s={s}")
        for geom_name, generator in GEOMETRIES.items():
            for n in ns:

                # ---- WARMUP ----
                warm_points = generator(n, seed=0)
                _ = run_trial(warm_points, s=s_values[0])
                # ----------------

                for trial in range(trials):
                    points = generator(n, seed=trial)

                    for s in s_values:
                        result = run_trial(points, s=s)
                        row = {
                            "geometry": geom_name,
                            "n": n,
                            "trial": trial,
                            "s": s,
                            **result,
                        }
                        writer.writerow(row)

                        print(f"{geom_name}, n={n}, trial={trial}, s={s}")

if __name__ == "__main__":
    run_experiments()
    gc.enable()
