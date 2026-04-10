# Streaming Convex Hull Filter

This repository contains the reference implementation and experimental code for the paper:

**“A Streaming Certificate-Based Reduction for Convex Hull Preservation in Planar Point Sets.”**

The code implements a conservative, single-pass geometric filter that discards points certified interior to the convex hull while preserving all true hull vertices. Exact hull computation is then performed only once on the reduced set.

## Contents

- `relaxed_filter.py`  
  Core streaming filter implementation.

- `relaxed_filter_stress_test.py`  
  Stress tests on synthetic point distributions and arrival orders.

- `relaxed_filter_plots.py`  
  Script to reproduce all figures reported in the paper.

- `experiments.py`  
  Synthetic-data experiments comparing the proposed method with the Akl-Toussaint heuristic.

- `analyze_results.py`  
  Generates plots and derived summaries from the outputs of `experiments.py`.

- `nyc_benchmarks.py`  
  Real-world benchmark script using NYC Yellow Taxi trip data.

- `summarise_nyc.py`  
  Computes summary statistics from the NYC benchmark outputs.

- `scripts/`  
  Download scripts for the public NYC benchmark data.

## Requirements

- Python 3.8 or later
- NumPy
- Matplotlib
- GeoPandas

Install dependencies with:

```bash
pip install -r requirements.txt
```

All experiments use fixed random seeds where applicable to ensure deterministic results.

## Data

The real-data benchmark script nyc_benchmarks.py expects the NYC Yellow Taxi input files under:

```bash
dataset/nyc_yellow_2025_q2/
```

## Usage

To reproduce Figures 1 and 2 reported in the paper:

```bash
python relaxed_filter_plots.py
```

## License
This code is released under the MIT License.