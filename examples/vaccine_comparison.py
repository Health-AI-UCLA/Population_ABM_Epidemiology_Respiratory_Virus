#!/usr/bin/env python3
"""
Vaccine comparison example for COVID-19 ABM.
"""

import sys
import os
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covid_abm import (
    OpenABMCovid19, 
    DiseaseParameters, 
    VaccineParameters
)

def compare_vaccine_types():
    """Compare different vaccine types"""
    print("🦠 Comparing vaccine types...")
    
    # Base parameters
    population_size = 50000
    days = 180
    n_seeds = 20
    
    # Vaccine scenarios
    scenarios = {
        "No Vaccine": VaccineParameters(vaccine_type="none"),
        "Sterilizing": VaccineParameters(
            vaccine_type="sterilizing",
            sterilizing_efficacy_infection=0.95,
            vaccination_rate_by_age=[0.01] * 9  # 1% daily vaccination rate
        ),
        "Non-Sterilizing": VaccineParameters(
            vaccine_type="non_sterilizing",
            non_sterilizing_efficacy_infection_dose2=0.25,
            non_sterilizing_efficacy_severe_dose2=0.90,
            vaccination_rate_by_age=[0.01] * 9
        )
    }
    
    results = {}
    
    for scenario_name, vaccine_params in scenarios.items():
        print(f"  Running scenario: {scenario_name}")
        
        # Create model
        model = OpenABMCovid19(
            population_size=population_size,
            vaccine_params=vaccine_params
        )
        
        # Run simulation
        simulation_results = model.run_simulation(
            days=days, 
            n_seeds=n_seeds, 
            verbose=False
        )
        
        results[scenario_name] = simulation_results
    
    # Plot comparison
    plot_vaccine_comparison(results)
    
    return results

def plot_vaccine_comparison(results):
    """Plot vaccine comparison results"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Vaccine Type Comparison', fontsize=16)
    
    # Plot 1: Cumulative infections
    ax1 = axes[0, 0]
    for scenario, data in results.items():
        cumulative_infected = [sum(data['new_infections'][:i+1]) 
                             for i in range(len(data['day']))]
        ax1.plot(data['day'], cumulative_infected, label=scenario, linewidth=2)
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Cumulative Infections')
    ax1.set_title('Cumulative Infections')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Daily new infections
    ax2 = axes[0, 1]
    for scenario, data in results.items():
        ax2.plot(data['day'], data['new_infections'], label=scenario, linewidth=2)
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Daily New Infections')
    ax2.set_title('Daily New Infections')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Hospitalizations
    ax3 = axes[1, 0]
    for scenario, data in results.items():
        ax3.plot(data['day'], data['hospitalized'], label=scenario, linewidth=2)
    ax3.set_xlabel('Day')
    ax3.set_ylabel('Hospitalized')
    ax3.set_title('Hospitalizations')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Deaths
    ax4 = axes[1, 1]
    for scenario, data in results.items():
        ax4.plot(data['day'], data['dead'], label=scenario, linewidth=2)
    ax4.set_xlabel('Day')
    ax4.set_ylabel('Deaths')
    ax4.set_title('Cumulative Deaths')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n📊 Summary Statistics:")
    print("=" * 50)
    for scenario, data in results.items():
        total_infected = sum(data['new_infections'])
        total_deaths = data['dead'][-1]
        peak_hospitalized = max(data['hospitalized'])
        
        print(f"{scenario}:")
        print(f"  Total infected: {total_infected:,}")
        print(f"  Total deaths: {total_deaths:,}")
        print(f"  Peak hospitalized: {peak_hospitalized:,}")
        print()

def main():
    """Main function"""
    print("🏥 COVID-19 ABM Vaccine Comparison")
    print("=" * 50)
    
    try:
        results = compare_vaccine_types()
        print("✅ Vaccine comparison completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
