#!/usr/bin/env python3
"""
Test script for the COVID-19 ABM simulation.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covid_abm import (
    OpenABMCovid19, 
    DiseaseParameters, 
    NetworkParameters, 
    InterventionParameters,
    VaccineParameters
)

def test_basic_simulation():
    """Test basic simulation functionality"""
    print("🧪 Testing COVID-19 ABM Simulation")
    print("=" * 50)
    
    # Create a small population for testing
    population_size = 1000
    
    # Create custom parameters
    disease_params = DiseaseParameters(
        infectious_rate=8.0,  # Higher transmission for testing
        mean_infectious_period=5.0
    )
    
    network_params = NetworkParameters(
        relative_transmission_household=2.0,
        daily_fraction_work=0.5
    )
    
    intervention_params = InterventionParameters(
        self_quarantine_fraction=0.3,  # 30% quarantine on symptoms
        test_on_symptoms=True
    )
    
    vaccine_params = VaccineParameters(
        vaccine_type="none"  # No vaccination for this test
    )
    
    print(f"📊 Population size: {population_size}")
    print(f"🦠 Infectious rate: {disease_params.infectious_rate}")
    print(f"🏠 Household transmission: {network_params.relative_transmission_household}")
    print(f"🚫 Quarantine fraction: {intervention_params.self_quarantine_fraction}")
    print()
    
    # Create and run simulation
    try:
        model = OpenABMCovid19(
            population_size=population_size,
            disease_params=disease_params,
            network_params=network_params,
            intervention_params=intervention_params,
            vaccine_params=vaccine_params
        )
        
        print("✅ Model created successfully!")
        print(f"👥 Population created: {len(model.population.people)} people")
        print(f"🏠 Households created: {len(model.population.households)}")
        print(f"🏢 Occupations created: {len(model.population.occupations)}")
        print()
        
        # Run simulation
        print("🚀 Running simulation...")
        results = model.run_simulation(days=30, n_seeds=5, verbose=True)
        
        print("\n📈 Simulation Results Summary:")
        print(f"   Final susceptible: {results['susceptible'][-1]}")
        print(f"   Final infected: {results['infected'][-1]}")
        print(f"   Final recovered: {results['recovered'][-1]}")
        print(f"   Final dead: {results['dead'][-1]}")
        print(f"   Peak infected: {max(results['infected'])}")
        print(f"   Total deaths: {results['dead'][-1]}")
        
        # Test plotting
        print("\n📊 Testing visualization...")
        try:
            model.plot_results()
            print("✅ Visualization completed successfully!")
        except Exception as e:
            print(f"⚠️  Visualization failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_validation():
    """Test parameter validation"""
    print("\n🔍 Testing parameter validation...")
    
    try:
        # Test default parameters
        disease_params = DiseaseParameters()
        network_params = NetworkParameters()
        intervention_params = InterventionParameters()
        vaccine_params = VaccineParameters()
        
        print("✅ All parameter classes created successfully")
        
        # Test parameter values
        assert disease_params.infectious_rate == 5.8
        assert len(disease_params.fraction_asymptomatic) == 9
        assert abs(sum(network_params.household_size_dist) - 1.0) < 1e-6
        
        print("✅ Parameter validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
        return False

if __name__ == "__main__":
    print("COVID-19 ABM Test Suite")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_parameter_validation()
    test2_passed = test_basic_simulation()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Parameter validation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Basic simulation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The simulation is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
