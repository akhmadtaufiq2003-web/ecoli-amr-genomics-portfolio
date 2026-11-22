#!/usr/bin/env bash
# Retrieve ONLY accessions listed in the validated public-assembly manifest.
set -euo pipefail
command -v datasets >/dev/null || { echo 'ERROR: install NCBI Datasets CLI v2 first' >&2; exit 2; }
command -v unzip >/dev/null || { echo 'ERROR: install unzip first' >&2; exit 2; }
python3 scripts/validate_manifest.py --manifest data/manifest.csv
mkdir -p data/raw data/assemblies results/logs
datasets --version > results/logs/datasets_version.txt
datasets download genome accession --inputfile data/accessions.txt --include genome --filename data/raw/ncbi_assemblies.zip
unzip -oq data/raw/ncbi_assemblies.zip -d data/raw/ncbi_package
python3 scripts/stage_assemblies.py --manifest data/manifest.csv --package-dir data/raw/ncbi_package
