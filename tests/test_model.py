"""
Integration tests for the main model.
"""

import pytest
from covid_abm import OpenABMCovid19, DiseaseParameters

class TestMainModel:
    def test_model_initialization(self):
        model = OpenABMCovid19(population_size=1000)
        assert model.population.size == 1000
        assert len(model.population.people) == 1000
    
    def test_simulation_run(self):
        model = OpenABMCovid19(population_size=1000)
        results = model.run_simulation(days=30, n_seeds=5, verbose=False)
        assert len(results['day']) == 30
    
    def test_vaccine_scenarios(self):
        # Test different vaccine configurations
        pass
