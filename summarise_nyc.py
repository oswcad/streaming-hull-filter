import pandas as pd

# Load results
df = pd.read_csv("nyc_results.csv")

# Compute speedups
df["speedup_relaxed"] = df["hull_time_full"] / df["total_time_relaxed"]
df["speedup_akl"] = df["hull_time_full"] / df["total_time_akl"]

# Group by dataset size and arrival order
grouped = df.groupby(["n", "arrival_order"])

summary = grouped.agg({
    "relaxed_ratio": ["mean", "std"],
    "akl_ratio": ["mean", "std"],
    "total_time_relaxed": ["mean", "std"],
    "total_time_akl": ["mean", "std"],
    "hull_time_full": ["mean", "std"],
    "speedup_relaxed": ["mean", "std"],
    "speedup_akl": ["mean", "std"],
}).reset_index()

# Flatten column names
summary.columns = [
    "_".join(col).strip("_") for col in summary.columns.values
]

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print(summary)
