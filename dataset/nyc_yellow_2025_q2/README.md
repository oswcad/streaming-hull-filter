This directory is expected to contain the public NYC benchmark data:

- yellow_tripdata_2025-03.parquet
- yellow_tripdata_2025-04.parquet
- yellow_tripdata_2025-05.parquet
- taxi_zones.shp
- taxi_zones.shx
- taxi_zones.dbf

Use the download scripts in `scripts/` to populate this directory.

Populate this directory using:

- `scripts/download_nyc_tripdata.sh`
- `scripts/download_nyc_taxizones.sh`