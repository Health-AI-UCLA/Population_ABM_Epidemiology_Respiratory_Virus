"""
Command-line interface for COVID-19 ABM.
"""

import argparse
import sys
from . import OpenABMCovid19, DiseaseParameters, NetworkParameters, InterventionParameters, VaccineParameters

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="COVID-19 Agent-Based Model")
    
    parser.add_argument("--population-size", type=int, default=100000,
                       help="Population size (default: 100000)")
    parser.add_argument("--days", type=int, default=150,
                       help="Simulation days (default: 150)")
    parser.add_argument("--seeds", type=int, default=10,
                       help="Number of initial seeds (default: 10)")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    
    # Disease parameters
    parser.add_argument("--infectious-rate", type=float, default=5.8,
                       help="Infectious rate (default: 5.8)")
    
    # Intervention parameters
    parser.add_argument("--quarantine-fraction", type=float, default=0.0,
                       help="Self-quarantine fraction (default: 0.0)")
    parser.add_argument("--test-on-symptoms", action="store_true",
                       help="Test on symptoms")
    
    # Vaccine parameters
    parser.add_argument("--vaccine-type", choices=["none", "sterilizing", "non_sterilizing"],
                       default="none", help="Vaccine type")
    
    args = parser.parse_args()
    
    # Create parameters
    disease_params = DiseaseParameters(infectious_rate=args.infectious_rate)
    intervention_params = InterventionParameters(
        self_quarantine_fraction=args.quarantine_fraction,
        test_on_symptoms=args.test_on_symptoms
    )
    vaccine_params = VaccineParameters(vaccine_type=args.vaccine_type)
    
    # Create and run model
    model = OpenABMCovid19(
        population_size=args.population_size,
        disease_params=disease_params,
        intervention_params=intervention_params,
        vaccine_params=vaccine_params
    )
    
    results = model.run_simulation(
        days=args.days,
        n_seeds=args.seeds,
        verbose=args.verbose
    )
    
    print(f"Simulation completed. Final infected: {results['infected'][-1]}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
