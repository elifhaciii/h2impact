#!/usr/bin/env python3
"""
Plot monthly electricity demand for a given country.

Usage:
  python plot_monthly_demand.py --input energy_demand.csv --country DE

Dependencies:
  pip install pandas matplotlib
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Plot monthly electricity demand for a country.")
    parser.add_argument("--input", "-i", required=True, help="Path to electricity_demand.csv")
    parser.add_argument("--country", "-c", required=True, help="Country code, e.g., DE")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        demand = pd.read_csv(args.input, index_col=0, parse_dates=True)
    except Exception as e:
        print(f"Failed to load CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.country not in demand.columns:
        print(f"Country code '{args.country}' not found in the CSV columns.", file=sys.stderr)
        print(f"Available columns: {', '.join(demand.columns)}", file=sys.stderr)
        sys.exit(1)

    # Resample to monthly total and rename index to month names
    monthly_demand = demand[args.country].resample("M").sum()
    monthly_demand.index = monthly_demand.index.strftime('%B')

    # Plotting
    monthly_demand.plot(kind="bar", color="red", figsize=(10, 6))
    plt.title(f"Monthly Electricity Demand - {args.country}")
    plt.xlabel("Month")
    plt.ylabel("Total Demand (MWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
