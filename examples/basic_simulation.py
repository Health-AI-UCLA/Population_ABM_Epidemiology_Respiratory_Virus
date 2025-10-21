"""
Basic simulation example using the new modular structure.
"""

from covid_abm import (
    OpenABMCovid19, 
    DiseaseParameters, 
    NetworkParameters, 
    InterventionParameters,
    VaccineParameters
)

def main():
    """Run a basic COVID-19 simulation"""
    
    # Create custom parameters
    disease_params = DiseaseParameters(
        infectious_rate=6.0,  # Slightly higher transmission
        mean_infectious_period=5.5
    )
    
    network_params = NetworkParameters(
        relative_transmission_household=2.5,  # Higher household transmission
        daily_fraction_work=0.6  # More workplace activity
    )
    
    intervention_params = InterventionParameters(
        self_quarantine_fraction=0.8,  # 80% self-quarantine on symptoms
        test_on_symptoms=True,
        trace_on_positive=True
    )
    
    vaccine_params = VaccineParameters(
        vaccine_type="non_sterilizing",
        non_sterilizing_efficacy_infection_dose2=0.25,
        non_sterilizing_efficacy_severe_dose2=0.90
    )
    
    # Create and run simulation
    model = OpenABMCovid19(
        population_size=10000,
        disease_params=disease_params,
        network_params=network_params,
        intervention_params=intervention_params,
        vaccine_params=vaccine_params
    )
    
    # Run simulation
    results = model.run_simulation(days=150, n_seeds=5, verbose=True)
    
    # Plot results
    model.plot_results()
    
    return results

if __name__ == "__main__":
    results = main()