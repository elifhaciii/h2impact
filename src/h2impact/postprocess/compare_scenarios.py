import pypsa
import pandas as pd
import matplotlib.pyplot as plt

def ask_file(prompt):
    import os
    while True:
        f = input(prompt)
        if os.path.exists(f):
            return f
        print("File does not exist. Try again.")

print("=== PyPSA-Eur H2 / no-H2 Scenario Comparison ===")
file_h2 = ask_file("Enter path to H2-enabled .nc file: ")
file_noh2 = ask_file("Enter path to no-H2 .nc file: ")

print("Loading networks...")
net_h2 = pypsa.Network(file_h2)
net_noh2 = pypsa.Network(file_noh2)

def get_total_cost(net):
    # May need to adapt depending on network version
    return net.objective if hasattr(net, 'objective') else net.statistics.at['total', 'objective']

def generation_by_carrier(net):
    return net.generators.groupby("carrier").p_nom_opt.sum()

def capacity_by_carrier(net):
    return net.generators.groupby("carrier").p_nom_opt.sum()

def total_emissions(net):
    try:
        return net.global_constraints.query('type == "primary_emission"')["constant"].sum()
    except Exception:
        return "Not available"

# --- 1. Total Cost ---
costs = pd.DataFrame({
    "no-H2": [get_total_cost(net_noh2)],
    "H2-enabled": [get_total_cost(net_h2)]
}, index=["Total System Cost"])

print("\n--- Total System Cost ---")
print(costs)

# --- 2. Generation by Carrier ---
gen = pd.DataFrame({
    "no-H2": generation_by_carrier(net_noh2),
    "H2-enabled": generation_by_carrier(net_h2)
}).fillna(0)

print("\n--- Installed Capacity by Carrier (MW) ---")
print(gen)

# --- 3. Installed Capacity by Carrier (MW) ---
cap = pd.DataFrame({
    "no-H2": capacity_by_carrier(net_noh2),
    "H2-enabled": capacity_by_carrier(net_h2)
}).fillna(0)
print("\n--- Installed Capacity by Carrier (MW) ---")
print(cap)

# --- 4. CO2 Emissions ---
emissions = pd.DataFrame({
    "no-H2": [total_emissions(net_noh2)],
    "H2-enabled": [total_emissions(net_h2)]
}, index=["CO2 emissions"])
print("\n--- CO2 Emissions ---")
print(emissions)

# --- 5. Plot (optional) ---
plt.figure(figsize=(10,5))
gen.plot.bar()
plt.title("Installed Capacity by Carrier")
plt.ylabel("MW")
plt.tight_layout()
plt.show()
