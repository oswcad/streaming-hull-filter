#!/usr/bin/env python3
"""
Relaxed streaming convex hull filter with rejection and selective insertion.

Design principles:
- One-pass streaming
- Unordered input
- Maintain convex upper and lower envelopes
- Reject a point only with a sandwich certificate
- Insert a point only if it expands an envelope
- No full hull reconstruction
- Look-ahead parameter s ∈ {1, 2}

Guarantee:
    Hull(P) ⊆ R
"""

import random
import bisect
from typing import List, Tuple
import time

Point = Tuple[float, float]

# ------------------------------------------------------------
# Geometry
# ------------------------------------------------------------

def orient(a: Point, b: Point, c: Point) -> float:
    """Signed area * 2 of triangle (a,b,c)."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


# ------------------------------------------------------------
# Convex envelope insertion (local, no cascading)
# ------------------------------------------------------------

def try_insert_upper(chain: List[Point], p: Point):
    """Insert p into upper envelope if it preserves convexity."""
    i = bisect.bisect_left(chain, p)
    if 0 < i < len(chain):
        if orient(chain[i - 1], p, chain[i]) <= 0:
            return
    chain.insert(i, p)

    # local convexity repair (single hop)
    if i >= 2 and orient(chain[i - 2], chain[i - 1], chain[i]) <= 0:
        del chain[i - 1]
    if i + 2 < len(chain) and orient(chain[i], chain[i + 1], chain[i + 2]) <= 0:
        del chain[i + 1]


def try_insert_lower(chain: List[Point], p: Point):
    """Insert p into lower envelope if it preserves convexity."""
    i = bisect.bisect_left(chain, p)
    if 0 < i < len(chain):
        if orient(chain[i - 1], p, chain[i]) >= 0:
            return
    chain.insert(i, p)

    # local convexity repair (single hop)
    if i >= 2 and orient(chain[i - 2], chain[i - 1], chain[i]) >= 0:
        del chain[i - 1]
    if i + 2 < len(chain) and orient(chain[i], chain[i + 1], chain[i + 2]) >= 0:
        del chain[i + 1]


# ------------------------------------------------------------
# Relaxed streaming filter
# ------------------------------------------------------------

class RelaxedHullFilter:
    def __init__(self, s: int = 1):
        assert s in (1, 2)
        self.s = s
        self.upper: List[Point] = []
        self.lower: List[Point] = []
        self.buffer: List[Point] = []
        self.kept: List[Point] = []

    def _sandwich_reject(self, p: Point) -> bool:
        """Reject p if sandwiched between upper and lower envelopes."""
        if len(self.upper) < 2 or len(self.lower) < 2:
            return False

        iu = bisect.bisect_left(self.upper, p)
        il = bisect.bisect_left(self.lower, p)

        if 0 < iu < len(self.upper) and 0 < il < len(self.lower):
            u0, u1 = self.upper[iu - 1], self.upper[iu]
            l0, l1 = self.lower[il - 1], self.lower[il]

            above_lower = orient(l0, p, l1) >= 0
            below_upper = orient(u0, p, u1) <= 0

            return above_lower and below_upper

        return False

    def _process_point(self, p: Point):
        if self._sandwich_reject(p):
            return  # safely discard

        self.kept.append(p)
        try_insert_upper(self.upper, p)
        try_insert_lower(self.lower, p)

    def add(self, p: Point):
        self.buffer.append(p)
        if len(self.buffer) == self.s:
            for q in self.buffer:
                self._process_point(q)
            self.buffer.clear()

    def finalize(self):
        for p in self.buffer:
            self._process_point(p)
        self.buffer.clear()

    def candidate_set(self) -> List[Point]:
        return list(set(self.kept))


# ------------------------------------------------------------
# Reference convex hull (Andrew)
# ------------------------------------------------------------

def convex_hull(points: List[Point]) -> List[Point]:
    pts = sorted(points)
    if len(pts) <= 1:
        return pts

    lower = []
    for p in pts:
        while len(lower) >= 2 and orient(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and orient(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


# ------------------------------------------------------------
# Test driver
# ------------------------------------------------------------

def random_unique_points(n: int, seed=0) -> List[Point]:
    # random.seed(seed) # for reproducible
    random.seed(time.time())
    pts = set()
    while len(pts) < n:
        pts.add((round(random.random(), 6), round(random.random(), 6)))
    return list(pts)


if __name__ == "__main__":
    N = 10000
    pts = random_unique_points(N, seed=1)

    for s in (1, 2):
        filt = RelaxedHullFilter(s=s)
        for p in pts:
            filt.add(p)
        filt.finalize()

        R = filt.candidate_set()
        hull_R = sorted(convex_hull(R))
        hull_all = sorted(convex_hull(pts))

        print(f"\n=== s = {s} ===")
        print(f"Total points:        {N}")
        print(f"Kept after filter:   {len(R)}")
        print(f"Reduction ratio r/n: {len(R)/N:.3f}")
        print(f"Hull size:           {len(hull_all)}")
        print("Hull preserved:", hull_R == hull_all)