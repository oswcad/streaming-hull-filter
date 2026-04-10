#!/usr/bin/env python3
"""
Post-processing and plotting for convex hull filter experiments.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

INPUT_CSV = "results.csv"

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

df = pd.read_csv(INPUT_CSV)

# Compute speedups
df["speedup_relaxed"] = df["hull_time_full"] / df["total_time_relaxed"]
df["speedup_akl"] = df["hull_time_full"] / df["total_time_akl"]

# ------------------------------------------------------------
# Aggregate statistics
# ------------------------------------------------------------

group_cols = ["geometry", "n", "s"]

summary = (
    df.groupby(group_cols)
    .agg({
        "relaxed_ratio": ["mean", "std"],
        "akl_ratio": ["mean", "std"],
        "total_time_relaxed": ["mean", "std"],
        "total_time_akl": ["mean", "std"],
        "hull_time_full": ["mean"],
        "speedup_relaxed": ["mean", "std"],
        "speedup_akl": ["mean", "std"],
    })
)

summary.to_csv("summary_statistics.csv")

print(summary)

# ------------------------------------------------------------
# Plot 1: Reduction ratio vs n
# ------------------------------------------------------------

for geom in df["geometry"].unique():
    sub = df[df["geometry"] == geom]

    fig, ax = plt.subplots()

    for method, col in [("Relaxed", "relaxed_ratio"),
                        ("Akl", "akl_ratio")]:

        means = sub.groupby("n")[col].mean()
        stds = sub.groupby("n")[col].std()

        ax.errorbar(
            means.index,
            means.values,
            yerr=stds.values,
            marker='o',
            capsize=4,
            label=method
        )

    ax.set_title(f"Reduction ratio vs n ({geom})")
    ax.set_xlabel("n")
    ax.set_ylabel("Retained ratio r/n")
    ax.legend()
    ax.grid(True)
    plt.savefig(f"reduction_{geom}.png")
    plt.close()

# ------------------------------------------------------------
# Plot 2: Total runtime vs n
# ------------------------------------------------------------

for geom in df["geometry"].unique():
    sub = df[df["geometry"] == geom]

    fig, ax = plt.subplots()

    for method, col in [("Relaxed", "total_time_relaxed"),
                        ("Akl", "total_time_akl"),
                        ("Hull only", "hull_time_full")]:

        means = sub.groupby("n")[col].mean()
        ax.plot(means.index, means.values, marker='o', label=method)

    ax.set_title(f"Total runtime vs n ({geom})")
    ax.set_xlabel("n")
    ax.set_ylabel("Time (seconds)")
    ax.legend()
    ax.grid(True)
    plt.savefig(f"runtime_{geom}.png")
    plt.close()

# ------------------------------------------------------------
# Plot 3: Speedup vs n
# ------------------------------------------------------------

for geom in df["geometry"].unique():
    sub = df[df["geometry"] == geom]

    fig, ax = plt.subplots()

    for method, col in [("Relaxed", "speedup_relaxed"),
                        ("Akl", "speedup_akl")]:

        means = sub.groupby("n")[col].mean()
        ax.plot(means.index, means.values, marker='o', label=method)

    ax.axhline(1.0, linestyle='--')
    ax.set_title(f"Speedup over full hull ({geom})")
    ax.set_xlabel("n")
    ax.set_ylabel("Speedup")
    ax.legend()
    ax.grid(True)
    plt.savefig(f"speedup_{geom}.png")
    plt.close()

print("Plots generated.")
