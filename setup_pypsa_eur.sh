#!/bin/bash

echo "------ PyPSA-Eur Setup Script ------"

# Step 1: Ensure external/ exists and clone PyPSA-Eur if needed
if [ ! -d "external" ]; then
    mkdir external
    echo "Created external/ directory."
fi

cd external

if [ ! -d "pypsa-eur" ]; then
    echo "Cloning PyPSA-Eur repository..."
    git clone https://github.com/PyPSA/pypsa-eur.git
else
    echo "PyPSA-Eur repository already exists, skipping clone."
fi

cd pypsa-eur

# Step 2: Ask user for platform (macOS, Linux, Windows)
echo "Which platform are you using?"
echo "1) Linux (Intel/AMD)"
echo "2) macOS (Intel/AMD)"
echo "3) macOS (Apple Silicon M1/M2/ARM)"
echo "4) Windows"
read -p "Select 1/2/3/4 [default: 1]: " PLATFORM

LOCKFILE="envs/linux-64.lock.yaml"
if [ "$PLATFORM" == "2" ]; then
    LOCKFILE="envs/osx-64.lock.yaml"
elif [ "$PLATFORM" == "3" ]; then
    LOCKFILE="envs/osx-arm64.lock.yaml"
elif [ "$PLATFORM" == "4" ]; then
    LOCKFILE="envs/win-64.lock.yaml"
fi

echo "Using lockfile: $LOCKFILE"

# Step 3: Update conda and create environment
conda update -y conda
conda env create -f $LOCKFILE

# Step 4: Activate environment and install solver
source $(conda info --base)/etc/profile.d/conda.sh
conda activate pypsa-eur

echo "Installing HiGHS solver..."
conda install -y -c conda-forge highs

echo "-------------------------------------------------------------"
echo "PyPSA-Eur environment setup complete!"
echo "You can now run Snakemake or Python scripts for PyPSA-Eur."
echo "Make sure to activate the environment before each run:"
echo "   conda activate pypsa-eur"
echo "-------------------------------------------------------------"
