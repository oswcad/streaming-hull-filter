#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p dataset/nyc_yellow_2025_q2

cd "$tmpdir"
wget "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
unzip taxi_zones.zip

cp taxi_zones/taxi_zones.shp "$OLDPWD/dataset/nyc_yellow_2025_q2/"
cp taxi_zones/taxi_zones.shx "$OLDPWD/dataset/nyc_yellow_2025_q2/"
cp taxi_zones/taxi_zones.dbf "$OLDPWD/dataset/nyc_yellow_2025_q2/"

