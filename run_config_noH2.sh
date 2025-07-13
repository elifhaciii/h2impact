#!/bin/bash
# Usage: bash run_pypsaeur_nohydrogen.sh <config_yaml_path>
# Example: bash run_pypsaeur_nohydrogen.sh ../../src/h2impact/configs/config_no_H2_fr-2013-03.yaml

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: bash $0 <config_yaml_path>"
    exit 1
fi

CONFIG="$1"

# Extract run_name, clusters, planning_horizon, country, cutout from config file
run_name=$(grep -m1 '^  name:' "$CONFIG" | awk '{print $2}' | tr -d '"')
clusters=$(grep -A2 '^scenario:' "$CONFIG" | grep -m1 '-' | awk '{print $2}')
planning_horizon=$(grep -A2 '^planning_horizons:' "$CONFIG" | grep -m1 '-' | awk '{print $2}')
country=$(grep -A2 '^countries:' "$CONFIG" | grep -m1 '-' | awk '{print tolower($2)}')
cutout=$(grep -A2 '^atlite:' "$CONFIG" | grep -m1 'default_cutout:' | awk '{print $2}' | tr -d '"')

# Fallback defaults
[ -z "$clusters" ] && clusters="5"
[ -z "$planning_horizon" ] && planning_horizon="2030"

# Change to pypsa-eur workflow directory
cd "$(dirname "$0")/external/pypsa-eur"

echo "Running Snakemake for: $CONFIG"
snakemake -j1 --configfile "$CONFIG"

# Result file pattern
RESULT_SRC="results/${run_name}/postnetworks/base_s_${clusters}___${planning_horizon}.nc"
RESULT_DST="../../results/${country}-${cutout}-nohydrogen-result.nc"

if [ -f "$RESULT_SRC" ]; then
    mkdir -p ../../results
    cp "$RESULT_SRC" "$RESULT_DST"
    echo "[OK] Copied result to: $RESULT_DST"
else
    echo "[ERROR] Result file not found: $RESULT_SRC"
    exit 2
fi
