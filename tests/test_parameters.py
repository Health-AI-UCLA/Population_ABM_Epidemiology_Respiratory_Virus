"""
Unit tests for parameter classes.
"""

import pytest
from covid_abm.models.parameters import DiseaseParameters, NetworkParameters

class TestDiseaseParameters:
    def test_default_parameters(self):
        params = DiseaseParameters()
        assert params.infectious_rate == pytest.approx(35.0)
        assert len(params.fraction_asymptomatic) == 9
        # Verify severity and immunity defaults align with literature-informed updates
        assert params.fraction_fatality[-1] == pytest.approx(0.15, rel=0.05)
        assert params.reinfection_protection_days == pytest.approx(180.0)
    
    def test_parameter_validation(self):
        # Test parameter bounds and validation
        pass

class TestNetworkParameters:
    def test_household_distribution(self):
        params = NetworkParameters()
        assert sum(params.household_size_dist) == pytest.approx(1.0)
        assert all(prob >= 0 for prob in params.household_size_dist)
    
    def test_network_consistency(self):
        # Test network parameter consistency
        pass
