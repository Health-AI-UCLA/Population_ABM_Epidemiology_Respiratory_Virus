"""
COVID-19 Agent-Based Model Package

A comprehensive epidemiological simulation framework for COVID-19 transmission,
immunity dynamics, and intervention analysis.
"""

__version__ = "1.0.0"
__author__ = "COVID-19 ABM Development Team"

from .models.main_model import OpenABMCovid19
from .models.parameters import DiseaseParameters, NetworkParameters, InterventionParameters, VaccineParameters
from .models.person import Person, DiseaseState
from .models.population import Population
from .analysis.ensemble import EnsembleSimulation
from .analysis.scenarios import ScenarioAnalyzer, PolicyAnalyzer
from .utils.cloud_deployment import CloudDeployment
from .utils.visualization import ModelVisualizer

__all__ = [
    'OpenABMCovid19',
    'DiseaseParameters', 'NetworkParameters', 'InterventionParameters', 'VaccineParameters',
    'Person', 'DiseaseState', 'Population',
    'EnsembleSimulation', 'ScenarioAnalyzer', 'PolicyAnalyzer',
    'CloudDeployment', 'ModelVisualizer'
]
