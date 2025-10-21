"""
Unit tests for parameter classes.
"""

import pytest
from covid_abm.models.parameters import DiseaseParameters, NetworkParameters

class TestDiseaseParameters:
    def test_default_parameters(self):
        params = DiseaseParameters()
        assert params.infectious_rate == 5.8
        assert len(params.fraction_asymptomatic) == 9
    
    def test_parameter_validation(self):
        # Test parameter bounds and validation
        pass

class TestNetworkParameters:
    def test_household_distribution(self):
        params = NetworkParameters()
        assert abs(sum(params.household_size_dist) - 1.0) < 1e-6
    
    def test_network_consistency(self):
        # Test network parameter consistency
        pass
