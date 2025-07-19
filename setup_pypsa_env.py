import os
import subprocess
from pathlib import Path

print("------ PyPSA-Eur Setup Script (Python) ------")

# Step 1: Ensure external/ exists
external_dir = Path("external")
pypsa_dir = external_dir / "pypsa-eur"

if not external_dir.exists():
    external_dir.mkdir()
    print("Created external/ directory.")

# Step 2: Clone PyPSA-Eur repo if needed
if not pypsa_dir.exists():
    print("Cloning PyPSA-Eur repository...")
    subprocess.run(["git", "clone", "https://github.com/PyPSA/pypsa-eur.git", str(pypsa_dir)])
else:
    print("PyPSA-Eur repository already exists, skipping clone.")

# Step 3: Platform prompt
print("Which platform are you using?")
print("1) Linux (Intel/AMD)")
print("2) macOS (Intel/AMD)")
print("3) macOS (Apple Silicon M1/M2/ARM)")
print("4) Windows")

try:
    platform_choice = int(input("Select 1/2/3/4 [default: 1]: ") or "1")
except ValueError:
    platform_choice = 1

lockfile_map = {
    1: "envs/linux-64.lock.yaml",
    2: "envs/osx-64.lock.yaml",
    3: "envs/osx-arm64.lock.yaml",
    4: "envs/win-64.lock.yaml",
}

lockfile = lockfile_map.get(platform_choice, lockfile_map[1])
print(f"Using lockfile: {lockfile}")

# Step 4: Run Conda commands
os.chdir(pypsa_dir)

print("Updating conda...")
subprocess.run(["conda", "update", "-y", "conda"])

print("Creating conda environment...")
subprocess.run(["conda", "env", "create", "-f", lockfile])

# Step 5: Activate and install HiGHS solver
conda_base = subprocess.check_output(["conda", "info", "--base"]).decode().strip()
conda_profile = Path(conda_base) / "etc" / "profile.d" / "conda.sh"

activation = f"source {conda_profile} && conda activate pypsa-eur && conda install -y -c conda-forge highs"

print("Installing HiGHS solver in pypsa-eur env...")
subprocess.run(["bash", "-c", activation])

print("\n-------------------------------------------------------------")
print("PyPSA-Eur environment setup complete!")
print("To use it in future sessions, run:")
print("   conda activate pypsa-eur")
print("-------------------------------------------------------------")

