#!/usr/bin/env python3
"""
Stress test matrix for the relaxed streaming convex hull filter.

Matrix:
  - 7 point distributions
  - 5 arrival orders

For each (distribution, order):
  - run relaxed filter
  - verify hull preservation
  - report reduction ratio r/n
"""

import random
import math
from typing import List, Tuple

from relaxed_filter import (
    RelaxedHullFilter,
    convex_hull,
    orient,
)

Point = Tuple[float, float]

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


DISTRIBUTIONS = {
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


ORDERS = {
    "random": order_random,
    "x": order_x,
    "x_rev": order_x_rev,
    "y": order_y,
    "zigzag": order_zigzag,
}

# ------------------------------------------------------------
# Stress test
# ------------------------------------------------------------

def run_test(n=1000, seed=0, s=1):
    print(f"\n=== Relaxed filter stress test (n={n}, s={s}) ===\n")

    for dname, dgen in DISTRIBUTIONS.items():
        base_pts = dgen(n, seed)
        true_hull = sorted(convex_hull(base_pts))

        print(f"[Distribution: {dname}]")

        for oname, order_fn in ORDERS.items():
            pts = base_pts.copy()
            pts = order_fn(pts)

            filt = RelaxedHullFilter(s=s)
            for p in pts:
                filt.add(p)
            filt.finalize()

            R = filt.candidate_set()
            hull_R = sorted(convex_hull(R))

            ok = hull_R == true_hull
            ratio = len(R) / n

            print(
                f"  {oname:8s} | kept {len(R):4d} | r/n={ratio:6.3f} | ok={ok}"
            )

        print()

# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    run_test(n=1000, seed=1, s=1)
    # Optional:
    run_test(n=1000, seed=1, s=2)