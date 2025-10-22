"""
Individual agent (Person) class for COVID-19 ABM.
"""

from enum import Enum
from typing import Set

class DiseaseState(Enum):
    SUSCEPTIBLE = 0
    PRESYMPTOMATIC = 1
    ASYMPTOMATIC = 2
    SYMPTOMATIC_MILD = 3
    SYMPTOMATIC_SEVERE = 4
    HOSPITALIZED = 5
    CRITICAL = 6
    RECOVERED_PROTECTED = 7
    RECOVERED_PARTIAL = 8
    RECOVERED_WANED = 9
    DEAD = 10

class Person:
    """Individual agent with disease, network, and intervention states"""
    
    def __init__(self, person_id: int, age_group: int, household_id: int):
        self.id = person_id
        self.age_group = age_group
        self.household_id = household_id
        self.occupation_id = None
        
        # Disease state
        self.disease_state = DiseaseState.SUSCEPTIBLE
        self.infection_day = -1
        self.days_infected = 0
        self.symptom_onset_day = -1
        
        # Disease progression flags
        self.will_be_asymptomatic = False
        self.will_be_mild = False
        self.will_be_hospitalised = False
        self.will_be_critical = False
        self.will_die = False
        
        # Disease timing
        self.time_to_symptoms = 0
        self.time_to_hospital = 0
        self.time_to_critical = 0
        self.time_to_death = 0
        self.time_to_recover = 0
        
        # Infectiousness
        self.infectious_profile = []
        self.individual_infectiousness_factor = 1.0
        
        # Immunity tracking
        self.recovery_day = -1
        self.reinfection_protection_end = -1
        self.severe_protection_level = 0.0
        self.infection_protection_level = 0.0
        self.num_infections = 0
        
        # Vaccination
        self.vaccination_doses = 0
        self.dose1_day = -1
        self.dose2_day = -1
        self.vaccine_type = "none"
        self.vaccine_protection_infection = 0.0
        self.vaccine_protection_severe = 0.0
        self.vaccine_protected_infection = False
        self.vaccine_protected_severe = False
        
        # Testing and tracing
        self.tested = False
        self.test_positive = False
        self.test_day = -1
        self.traced = False
        self.traced_day = -1
        
        # Quarantine
        self.quarantined = False
        self.quarantine_start_day = -1
        self.quarantine_reason = None
        
        # App usage
        self.has_app = False
        
        # Networks
        self.household_contacts: Set[int] = set()
        self.occupation_contacts: Set[int] = set()
        self.random_contacts: Set[int] = set()
        self.contact_history = [set() for _ in range(7)]
        
        # Daily interactions target
        self.daily_interactions_target = 0
