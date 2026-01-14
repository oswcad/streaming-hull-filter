# Streaming Convex Hull Filter

This repository contains the reference implementation and experimental code for the paper:

**“A Streaming Certificate-Based Reduction for Convex Hull Preservation in Planar Point Sets.”**

The code implements a conservative, single-pass geometric filter that discards points certified interior to the convex hull, while preserving all true hull vertices. Exact hull computation is performed only once on the reduced set.

## Contents

- `relaxed_filter.py`  
  Core streaming filter implementation.

- `relaxed_filter_stress_test.py`  
  Stress tests on synthetic point distributions and arrival orders.

- `relaxed_filter_plots.py`  
  Script to reproduce all figures reported in the paper.

## Requirements

- Python 3.8 or later
- NumPy
- Matplotlib

Install dependencies with:

```bash
pip install -r requirements.txt
```

## License
This code is released under the MIT License.