#!/usr/bin/env python3
"""
Generate two figures for the relaxed streaming convex hull filter.

Figure 1:
  - Mean reduction ratio (r/n) under RANDOM arrival
  - Across 7 geometric distributions

Figure 2:
  - Mean reduction ratio (r/n) across ARRIVAL ORDERS
  - For two representative distributions (uniform, gaussian)

Design goals:
  - One-pass streaming
  - Reproducible (fixed seed range)
  - Honest depiction of strengths and limits
"""

import random
import math
import statistics
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt

from relaxed_filter import RelaxedHullFilter, convex_hull

Point = Tuple[float, float]

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

N_POINTS = 1000
SEEDS = list(range(20))   # number of repetitions per condition
S = 1                     # fixed, final choice

# ------------------------------------------------------------
# Point distributions
# ------------------------------------------------------------

def uniform_square(n, seed):
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def gaussian_isotropic(n, seed):
    random.seed(seed)
    return [(random.gauss(0, 1), random.gauss(0, 1)) for _ in range(n)]

def gaussian_anisotropic(n, seed):
    random.seed(seed)
    return [(random.gauss(0, 3), random.gauss(0, 0.3)) for _ in range(n)]

def banana(n, seed):
    random.seed(seed)
    pts = []
    for _ in range(n):
        x = random.gauss(0, 1)
        y = x * x + random.gauss(0, 0.2)
        pts.append((x, y))
    return pts

def superellipse(n, seed, p=6):
    random.seed(seed)
    pts = []
    for _ in range(n):
        t = random.random() * 2 * math.pi
        x = math.copysign(abs(math.cos(t)) ** (2 / p), math.cos(t))
        y = math.copysign(abs(math.sin(t)) ** (2 / p), math.sin(t))
        pts.append((x, y))
    return pts

def annulus(n, seed):
    random.seed(seed)
    pts = []
    for _ in range(n):
        r = random.uniform(0.7, 1.0)
        t = random.random() * 2 * math.pi
        pts.append((r * math.cos(t), r * math.sin(t)))
    return pts

def clustered_outliers(n, seed):
    random.seed(seed)
    pts = []
    for _ in range(int(0.9 * n)):
        pts.append((random.gauss(0, 0.3), random.gauss(0, 0.3)))
    for _ in range(n - len(pts)):
        pts.append((random.uniform(-3, 3), random.uniform(-3, 3)))
    return pts


DISTRIBUTIONS: Dict[str, callable] = {
    "uniform": uniform_square,
    "gaussian": gaussian_isotropic,
    "anisotropic": gaussian_anisotropic,
    "banana": banana,
    "superellipse": superellipse,
    "annulus": annulus,
    "cluster+outliers": clustered_outliers,
}

# ------------------------------------------------------------
# Arrival orders
# ------------------------------------------------------------

def order_random(pts):
    random.shuffle(pts)
    return pts

def order_x(pts):
    return sorted(pts, key=lambda p: p[0])

def order_x_rev(pts):
    return sorted(pts, key=lambda p: -p[0])

def order_y(pts):
    return sorted(pts, key=lambda p: p[1])

def order_zigzag(pts):
    pts = sorted(pts, key=lambda p: p[0])
    return pts[::2] + pts[1::2][::-1]


ORDERS: Dict[str, callable] = {
    "random": order_random,
    "x": order_x,
    "x_rev": order_x_rev,
    "y": order_y,
    "zigzag": order_zigzag,
}

# ------------------------------------------------------------
# Core experiment utilities
# ------------------------------------------------------------

def run_filter(points: List[Point]) -> float:
    """Run relaxed filter and return reduction ratio r/n."""
    filt = RelaxedHullFilter(s=S)
    for p in points:
        filt.add(p)
    filt.finalize()
    R = filt.candidate_set()
    return len(R) / len(points)


def mean_std(values: List[float]):
    return statistics.mean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)

# ------------------------------------------------------------
# Figure 1: Random arrival, all distributions
# ------------------------------------------------------------

def figure_random_order():
    labels = []
    means = []
    stds = []

    for name, gen in DISTRIBUTIONS.items():
        ratios = []
        for seed in SEEDS:
            pts = gen(N_POINTS, seed)
            pts = order_random(pts)
            ratios.append(run_filter(pts))
        mu, sd = mean_std(ratios)
        labels.append(name)
        means.append(mu)
        stds.append(sd)

    plt.figure(figsize=(9, 4))
    plt.bar(labels, means)
    plt.ylabel("Mean reduction ratio r/n")
    plt.title("Relaxed streaming filter — random arrival")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
# Figure 2: Order sensitivity (two representative distributions)
# ------------------------------------------------------------

def figure_order_sensitivity():
    reps = {
        "uniform": uniform_square,
        "gaussian": gaussian_isotropic,
    }

    plt.figure(figsize=(9, 4))

    for name, gen in reps.items():
        order_labels = []
        means = []

        for oname, order_fn in ORDERS.items():
            ratios = []
            for seed in SEEDS:
                pts = gen(N_POINTS, seed)
                pts = order_fn(pts)
                ratios.append(run_filter(pts))
            mu, _ = mean_std(ratios)
            order_labels.append(oname)
            means.append(mu)

        plt.plot(order_labels, means, marker="o", label=name)

    plt.ylabel("Mean reduction ratio r/n")
    plt.title("Order sensitivity of relaxed streaming filter")
    plt.legend()
    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    figure_random_order()
    figure_order_sensitivity()
    