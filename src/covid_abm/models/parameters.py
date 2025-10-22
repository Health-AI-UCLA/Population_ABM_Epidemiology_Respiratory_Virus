"""
Parameter classes for COVID-19 agent-based model configuration.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class DiseaseParameters:
    """Parameters for disease progression and transmission"""
    # Infectiousness parameters
    infectious_rate: float = 35.0
    mean_infectious_period: float = 7.0
    sd_infectious_period: float = 2.5

    # Gamma distribution parameters for infectiousness curve
    infectiousness_shape: float = 2.0
    infectiousness_scale: float = 2.0

    # Relative infectiousness by disease severity
    asymptomatic_infectious_factor: float = 0.33
    mild_infectious_factor: float = 0.72
    severe_infectious_factor: float = 1.0

    # Individual infectiousness variation
    individual_infectiousness_sd: float = 0.4

    # Age-stratified disease progression probabilities
    fraction_asymptomatic: List[float] = field(default_factory=lambda: [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10])
    fraction_mild: List[float] = field(default_factory=lambda: [0.48, 0.50, 0.53, 0.55, 0.56, 0.54, 0.50, 0.45, 0.40])
    fraction_hospitalised: List[float] = field(default_factory=lambda: [0.015, 0.020, 0.035, 0.050, 0.080, 0.120, 0.180, 0.250, 0.300])
    fraction_critical: List[float] = field(default_factory=lambda: [0.004, 0.005, 0.010, 0.020, 0.040, 0.070, 0.100, 0.150, 0.200])
    fraction_fatality: List[float] = field(default_factory=lambda: [0.0002, 0.0005, 0.0010, 0.0020, 0.0050, 0.0100, 0.0300, 0.0800, 0.1500])

    # Age-stratified susceptibility
    relative_susceptibility: List[float] = field(default_factory=lambda: [0.4, 0.4, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

    # Time distributions
    mean_time_to_symptoms: float = 5.0
    sd_time_to_symptoms: float = 2.0
    mean_symptom_to_recover_mild: float = 8.0
    sd_symptom_to_recover_mild: float = 3.0
    mean_symptom_to_hospital: float = 6.5
    sd_symptom_to_hospital: float = 2.5
    mean_hospital_to_recover: float = 10.0
    sd_hospital_to_recover: float = 4.0
    mean_hospital_to_critical: float = 3.0
    sd_hospital_to_critical: float = 1.5
    mean_critical_to_death: float = 9.0
    sd_critical_to_death: float = 3.0
    mean_critical_to_recover: float = 14.0
    sd_critical_to_recover: float = 5.0
    mean_time_to_recover: float = 18.0
    sd_time_to_recover: float = 6.0
    mean_asymptomatic_to_recover: float = 12.0
    sd_asymptomatic_to_recover: float = 4.0

    # Immunity parameters
    reinfection_protection_days: float = 180.0
    severe_protection_days: float = 540.0
    severe_protection_decay_rate: float = 0.25
    reinfection_protection_level: float = 0.75
    partial_immunity_floor: float = 0.15

@dataclass 
class NetworkParameters:
    """Parameters for social interaction networks"""
    # Household sizes distribution
    household_size_dist: List[float] = field(default_factory=lambda: [0.28, 0.34, 0.16, 0.13, 0.06, 0.03])
    
    # Age-stratified mean daily interactions
    mean_daily_interactions: List[float] = field(default_factory=lambda: [11.8, 15.6, 14.6, 13.6, 14.7, 13.8, 10.2, 7.6, 4.0])
    
    # Occupation network parameters
    mean_work_interactions_child: float = 8.0
    mean_work_interactions_teen: float = 16.0
    mean_work_interactions_adult: float = 7.0
    mean_work_interactions_elderly: float = 2.0
    
    # Random interactions
    mean_random_interactions: List[float] = field(default_factory=lambda: [2.0, 3.0, 4.0, 4.0, 4.0, 4.0, 3.0, 2.0, 1.0])
    overdispersion_random: float = 0.62
    
    # Daily network participation
    daily_fraction_work: float = 0.5
    
    # Adult ratios in non-adult networks
    child_network_adults_ratio: float = 0.2
    elderly_network_adults_ratio: float = 0.2
    
    # Network transmission multipliers
    relative_transmission_household: float = 2.0
    relative_transmission_occupation: float = 1.0
    relative_transmission_random: float = 1.0

@dataclass
class InterventionParameters:
    """Parameters for non-pharmaceutical interventions"""
    # Self-isolation
    self_quarantine_fraction: float = 0.0
    self_quarantine_days: int = 7
    quarantine_household_on_symptoms: bool = False
    quarantine_compliance: float = 1.0
    quarantine_dropout_rate: float = 0.0
    
    # Testing
    test_sensitivity: float = 0.8
    test_specificity: float = 0.99
    test_delay_days: int = 1
    test_result_delay_days: int = 1
    test_on_symptoms: bool = False
    test_contacts: bool = False
    
    # Contact tracing
    app_users_fraction: List[float] = field(default_factory=lambda: [0.0] * 9)
    manual_tracing_coverage: float = 0.0
    trace_on_symptoms: bool = False
    trace_on_positive: bool = False
    contact_recall_household: float = 0.9
    contact_recall_occupation: float = 0.8
    contact_recall_random: float = 0.3
    tracing_delay_days: int = 2
    trace_household_contacts: bool = True
    trace_second_degree: bool = False
    
    # Lockdown/social distancing
    lockdown_occupation_multiplier: float = 1.0
    lockdown_random_multiplier: float = 1.0
    lockdown_household_multiplier: float = 1.0
    
    # Age-specific shielding
    shielding_elderly: bool = False
    shielding_contact_reduction: float = 0.5

@dataclass
class VaccineParameters:
    """Parameters for vaccination scenarios"""
    vaccine_type: str = "none"  # "sterilizing", "non_sterilizing", or "none"
    
    # Sterilizing vaccine
    sterilizing_efficacy_infection: float = 0.95
    sterilizing_protection_days: float = 1095.0
    sterilizing_decay_rate: float = 0.3
    
    # Non-sterilizing vaccine
    non_sterilizing_efficacy_infection_dose1: float = 0.20
    non_sterilizing_efficacy_infection_dose2: float = 0.20
    non_sterilizing_efficacy_severe_dose1: float = 0.80
    non_sterilizing_efficacy_severe_dose2: float = 0.95
    non_sterilizing_protection_days: float = 1095.0
    non_sterilizing_decay_rate: float = 0.3
    
    # Dosing schedule
    dose_interval_days: int = 28
    time_to_protection_dose1: int = 14
    time_to_protection_dose2: int = 7
    
    # Vaccination rates by age
    vaccination_rate_by_age: List[float] = field(default_factory=lambda: [0.0] * 9)
