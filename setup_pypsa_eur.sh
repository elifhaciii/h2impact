#!/bin/bash

# Step 1: Update conda
conda update -y conda

# Step 2: Create environment using the PyPSA-Eur lockfile (choose your platform as needed)
conda env create -f external/pypsa-eur/envs/linux-64.lock.yaml

# Step 3: Activate environment
conda activate pypsa-eur

# Step 4: Install the HiGHS solver (if not already installed)
conda install -y -c conda-forge highs

echo "-------------------------------------------------------------"
echo "PyPSA-Eur environment setup complete!"
echo "You can now run Snakemake or Python scripts for PyPSA-Eur."
echo "If you use another OS, select the matching lockfile in envs/."
echo "Make sure to activate the environment before each run:"
echo "   conda activate pypsa-eur"
echo "-------------------------------------------------------------"

