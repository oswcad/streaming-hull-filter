import os
import random
import pandas as pd
import numpy as np
from typing import List, Tuple
from experiments import run_trial   # assumes run_trial is in experiments.py

from pathlib import Path
import os

# -----------------------------
# CONFIG
# -----------------------------
REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("NYC_DATA_DIR", REPO_ROOT / "dataset" / "nyc_yellow_2025_q2"))

FILES = [
    "yellow_tripdata_2025-03.parquet",
    "yellow_tripdata_2025-04.parquet",
    "yellow_tripdata_2025-05.parquet",
]

SIZES = [50_000, 100_000, 250_000, 500_000]
ARRIVAL_ORDERS = ["chronological", "random", "longitude_sorted"]

REPETITIONS = 3
OUTPUT_CSV = "nyc_results.csv"

# -----------------------------
# DATA LOADING
# -----------------------------

# def load_nyc_points() -> np.ndarray:
#     frames = []
#     for fname in FILES:
#         path = os.path.join(DATA_DIR, fname)
#         df = pd.read_parquet(path, columns=["pickup_longitude", "pickup_latitude"])
#         df = df.dropna()

#         # Basic NYC bounding box sanity filter
#         df = df[
#             (df["pickup_longitude"].between(-75, -72)) &
#             (df["pickup_latitude"].between(40, 42))
#         ]

#         frames.append(df)

#     df_all = pd.concat(frames, ignore_index=True)
#     points = df_all[["pickup_longitude", "pickup_latitude"]].to_numpy()
#     return points

import geopandas as gpd

def load_nyc_points():
    # Load taxi zones
    zones_path = os.path.join(DATA_DIR, "taxi_zones.shp")
    zones = gpd.read_file(zones_path)

    # Compute centroids
    zones["centroid"] = zones.geometry.centroid
    zones["lon"] = zones["centroid"].x
    zones["lat"] = zones["centroid"].y

    zone_lookup = zones.set_index("LocationID")[["lon", "lat"]]

    frames = []
    for fname in FILES:
        path = os.path.join(DATA_DIR, fname)
        df = pd.read_parquet(path, columns=["PULocationID"])

        # Map zone → centroid
        df = df.join(zone_lookup, on="PULocationID")

        df = df.dropna()
        frames.append(df[["lon", "lat"]])

    df_all = pd.concat(frames, ignore_index=True)

    points = df_all.to_numpy()
    return points

# -----------------------------
# ARRIVAL ORDERING
# -----------------------------

def apply_arrival_order(points: np.ndarray, mode: str) -> List[Tuple[float, float]]:
    pts = points.copy()

    if mode == "random":
        np.random.shuffle(pts)

    elif mode == "longitude_sorted":
        pts = pts[np.argsort(pts[:, 0])]

    elif mode == "chronological":
        # natural dataset order (already chronological)
        pass

    else:
        raise ValueError(f"Unknown arrival order: {mode}")

    return [tuple(p) for p in pts]


# -----------------------------
# MAIN BENCHMARK LOOP
# -----------------------------

def run_nyc_benchmark():
    print("Loading NYC dataset...")
    all_points = load_nyc_points()
    print(f"Total loaded points: {len(all_points)}")

    results = []

    for n in SIZES:
        for rep in range(REPETITIONS):

            # Random subsample
            idx = np.random.choice(len(all_points), n, replace=False)
            sample = all_points[idx]

            for order in ARRIVAL_ORDERS:
                print(f"Running n={n}, order={order}, rep={rep+1}")

                ordered_points = apply_arrival_order(sample, order)

                result = run_trial(ordered_points)

                result["arrival_order"] = order
                result["rep"] = rep + 1

                results.append(result)

    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved results to {OUTPUT_CSV}")


if __name__ == "__main__":
    run_nyc_benchmark()