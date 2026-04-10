#!/usr/bin/env bash
set -euo pipefail

mkdir -p nyc_yellow_2025_q2 && cd nyc_yellow_2025_q2

for m in 03 04 05; do
  wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-${m}.parquet
done