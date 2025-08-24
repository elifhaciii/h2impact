#!/usr/bin/env python3
"""
Visualize the state of charge (SoC) for hydrogen stores from a PyPSA network.

Usage:
  python visualize_h2_soc.py --input path/to/network.nc

Dependencies:
  pip install pypsa matplotlib
"""

import sys
import argparse
import pypsa
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot hydrogen store state of charge (SoC) over time."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to the PyPSA network .nc file"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Loading network from: {args.input}")
    try:
        n = pypsa.Network(args.input)
    except Exception as e:
        print(f"Error loading network: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter hydrogen stores
    h2_stores = n.stores[n.stores.carrier.str.contains("H2", case=False, na=False)]
    if h2_stores.empty:
        print("No hydrogen stores found in the network.")
        sys.exit(0)

    print("Hydrogen Stores Found:")
    print(h2_stores[["bus", "e_nom", "carrier"]])

    # Get time-series state of charge
    h2_soc = n.stores_t.e[h2_stores.index]

    # Plotting
    ax = h2_soc.plot(figsize=(10, 5),
                     title="Hydrogen Store State of Charge Over Time")
    ax.set_ylabel("State of Charge [MWh]")
    ax.set_xlabel("Time")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
