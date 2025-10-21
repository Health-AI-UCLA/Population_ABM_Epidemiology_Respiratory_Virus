"""
Main COVID-19 agent-based model class.
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from .person import Person, DiseaseState
from .population import Population
from .parameters import DiseaseParameters, NetworkParameters, InterventionParameters, VaccineParameters
from ..utils.visualization import ModelVisualizer

class OpenABMCovid19:
    """Main COVID-19 agent-based model with enhanced immunity and vaccination"""
    
    def __init__(self, 
                 population_size: int = 100000,
                 age_distribution: List[float] = None,
                 disease_params: DiseaseParameters = None,
                 network_params: NetworkParameters = None,
                 intervention_params: InterventionParameters = None,
                 vaccine_params: VaccineParameters = None):
        
        # Initialize parameters
        if age_distribution is None:
            age_distribution = [0.12, 0.11, 0.13, 0.13, 0.13, 0.13, 0.11, 0.08, 0.05]
        
        self.disease_params = disease_params or DiseaseParameters()
        self.network_params = network_params or NetworkParameters()
        self.intervention_params = intervention_params or InterventionParameters()
        self.vaccine_params = vaccine_params or VaccineParameters()
        
        # Create population
        self.population = Population(
            population_size, age_distribution, 
            self.network_params.household_size_dist, self.network_params
        )
        
        # Simulation state
        self.day = 0
        self.transmission_events = []
        self.daily_stats = self._initialize_stats()
        
        # Initialize visualizer
        self.visualizer = ModelVisualizer(self)
        
        # Initialize individual characteristics
        self._initialize_individual_characteristics()
    
    def run_simulation(self, days: int, n_seeds: int = 10, verbose: bool = True):
        """Run simulation with epidemic/endemic detection"""
        if verbose:
            print(f"Starting simulation: {self.population.size} people, {days} days, {n_seeds} seeds")
        
        # Initialize seeds
        self._initialize_seeds(n_seeds)
        
        # Run simulation
        for day in range(days):
            self.day = day
            self.step()
            self._record_daily_stats()
            
            if verbose and day % 10 == 0:
                infected = sum(1 for p in self.population.people.values() 
                             if p.disease_state in [DiseaseState.PRESYMPTOMATIC, DiseaseState.ASYMPTOMATIC, 
                                                   DiseaseState.SYMPTOMATIC_MILD, DiseaseState.SYMPTOMATIC_SEVERE,
                                                   DiseaseState.HOSPITALIZED, DiseaseState.CRITICAL])
                print(f"Day {day}: {infected} infected")
        
        if verbose:
            print("Simulation completed!")
        
        return self.daily_stats
    
    def step(self):
        """Execute one simulation step"""
        # Disease progression
        self._update_disease_progression()
        
        # Transmission
        self._transmission_step()
        
        # Interventions
        self._intervention_step()
        
        # Vaccination
        self._vaccination_step()
    
    def _initialize_seeds(self, n_seeds: int):
        """Initialize infection seeds"""
        susceptible_people = [p for p in self.population.people.values() 
                            if p.disease_state == DiseaseState.SUSCEPTIBLE]
        
        if len(susceptible_people) < n_seeds:
            n_seeds = len(susceptible_people)
        
        seeds = random.sample(susceptible_people, n_seeds)
        
        for person in seeds:
            person.disease_state = DiseaseState.PRESYMPTOMATIC
            person.infection_day = 0
            person.days_infected = 0
            person.num_infections += 1
            
            # Set disease progression
            self._set_disease_progression(person)
    
    def _set_disease_progression(self, person: Person):
        """Set disease progression for a newly infected person"""
        age_group = person.age_group
        
        # Determine disease severity
        rand = random.random()
        if rand < self.disease_params.fraction_asymptomatic[age_group]:
            person.will_be_asymptomatic = True
        elif rand < self.disease_params.fraction_mild[age_group]:
            person.will_be_mild = True
        elif rand < self.disease_params.fraction_hospitalised[age_group]:
            person.will_be_hospitalised = True
        elif rand < self.disease_params.fraction_critical[age_group]:
            person.will_be_critical = True
            person.will_die = random.random() < self.disease_params.fraction_fatality[age_group]
        
        # Set timing
        person.time_to_symptoms = max(1, int(np.random.gamma(
            self.disease_params.mean_time_to_symptoms**2 / self.disease_params.sd_time_to_symptoms**2,
            self.disease_params.sd_time_to_symptoms**2 / self.disease_params.mean_time_to_symptoms
        )))
        
        person.time_to_recover = max(1, int(np.random.gamma(
            self.disease_params.mean_time_to_recover**2 / self.disease_params.sd_time_to_recover**2,
            self.disease_params.sd_time_to_recover**2 / self.disease_params.mean_time_to_recover
        )))
    
    def _update_disease_progression(self):
        """Update disease states for all infected people"""
        for person in self.population.people.values():
            if person.disease_state == DiseaseState.SUSCEPTIBLE:
                continue
                
            person.days_infected += 1
            
            # Disease progression logic
            if person.disease_state == DiseaseState.PRESYMPTOMATIC:
                if person.days_infected >= person.time_to_symptoms:
                    if person.will_be_asymptomatic:
                        person.disease_state = DiseaseState.ASYMPTOMATIC
                    else:
                        person.disease_state = DiseaseState.SYMPTOMATIC_MILD
            
            elif person.disease_state == DiseaseState.SYMPTOMATIC_MILD:
                if person.will_be_hospitalised and person.days_infected >= person.time_to_symptoms + 2:
                    person.disease_state = DiseaseState.HOSPITALIZED
                elif person.days_infected >= person.time_to_recover:
                    person.disease_state = DiseaseState.RECOVERED_PROTECTED
                    person.recovery_day = self.day
            
            elif person.disease_state == DiseaseState.HOSPITALIZED:
                if person.will_be_critical and person.days_infected >= person.time_to_symptoms + 5:
                    person.disease_state = DiseaseState.CRITICAL
                elif person.days_infected >= person.time_to_recover:
                    person.disease_state = DiseaseState.RECOVERED_PROTECTED
                    person.recovery_day = self.day
            
            elif person.disease_state == DiseaseState.CRITICAL:
                if person.will_die and person.days_infected >= person.time_to_symptoms + 8:
                    person.disease_state = DiseaseState.DEAD
                elif person.days_infected >= person.time_to_recover + 5:
                    person.disease_state = DiseaseState.RECOVERED_PROTECTED
                    person.recovery_day = self.day
            
            elif person.disease_state == DiseaseState.ASYMPTOMATIC:
                if person.days_infected >= person.time_to_recover:
                    person.disease_state = DiseaseState.RECOVERED_PROTECTED
                    person.recovery_day = self.day
    
    def _transmission_step(self):
        """Handle disease transmission"""
        infectious_people = [p for p in self.population.people.values() 
                           if p.disease_state in [DiseaseState.PRESYMPTOMATIC, DiseaseState.ASYMPTOMATIC,
                                                 DiseaseState.SYMPTOMATIC_MILD, DiseaseState.SYMPTOMATIC_SEVERE]]
        
        for infectious_person in infectious_people:
            # Get contacts
            contacts = self._get_contacts(infectious_person)
            
            # Calculate transmission probability
            base_transmission = self.disease_params.infectious_rate / 1000  # Per contact per day
            
            # Adjust for disease severity
            if infectious_person.disease_state == DiseaseState.ASYMPTOMATIC:
                transmission_prob = base_transmission * self.disease_params.asymptomatic_infectious_factor
            elif infectious_person.disease_state == DiseaseState.SYMPTOMATIC_MILD:
                transmission_prob = base_transmission * self.disease_params.mild_infectious_factor
            else:
                transmission_prob = base_transmission * self.disease_params.severe_infectious_factor
            
            # Try to infect contacts
            for contact_id in contacts:
                contact = self.population.people[contact_id]
                
                if contact.disease_state == DiseaseState.SUSCEPTIBLE:
                    # Check susceptibility
                    susceptibility = self.disease_params.relative_susceptibility[contact.age_group]
                    
                    if random.random() < transmission_prob * susceptibility:
                        contact.disease_state = DiseaseState.PRESYMPTOMATIC
                        contact.infection_day = self.day
                        contact.days_infected = 0
                        contact.num_infections += 1
                        self._set_disease_progression(contact)
    
    def _get_contacts(self, person: Person) -> List[int]:
        """Get daily contacts for a person"""
        contacts = []
        
        # Household contacts
        household_contacts = self.population.households[person.household_id]
        contacts.extend([c for c in household_contacts if c != person.id])
        
        # Occupation contacts
        if person.occupation_id is not None:
            occupation_contacts = self.population.occupations[person.occupation_id]
            contacts.extend([c for c in occupation_contacts if c != person.id])
        
        # Random contacts
        n_random = int(self.network_params.mean_random_interactions[person.age_group])
        if n_random > 0:
            other_people = [p_id for p_id in self.population.people.keys() 
                          if p_id != person.id and p_id not in contacts]
            if other_people:
                random_contacts = random.sample(other_people, min(n_random, len(other_people)))
                contacts.extend(random_contacts)
        
        return contacts
    
    def _intervention_step(self):
        """Handle interventions (quarantine, testing, etc.)"""
        # Simple quarantine implementation
        if self.intervention_params.self_quarantine_fraction > 0:
            symptomatic_people = [p for p in self.population.people.values() 
                                if p.disease_state in [DiseaseState.SYMPTOMATIC_MILD, DiseaseState.SYMPTOMATIC_SEVERE]]
            
            for person in symptomatic_people:
                if not person.quarantined and random.random() < self.intervention_params.self_quarantine_fraction:
                    person.quarantined = True
                    person.quarantine_start_day = self.day
    
    def _vaccination_step(self):
        """Handle vaccination"""
        if self.vaccine_params.vaccine_type != "none":
            # Simple vaccination implementation
            unvaccinated = [p for p in self.population.people.values() 
                          if p.vaccination_doses == 0 and p.disease_state == DiseaseState.SUSCEPTIBLE]
            
            for person in unvaccinated:
                vaccination_rate = self.vaccine_params.vaccination_rate_by_age[person.age_group]
                if random.random() < vaccination_rate / 1000:  # Daily vaccination rate
                    person.vaccination_doses = 1
                    person.dose1_day = self.day
                    person.vaccine_type = self.vaccine_params.vaccine_type
    
    def _record_daily_stats(self):
        """Record daily statistics"""
        stats = {
            'susceptible': 0,
            'infected': 0,
            'recovered': 0,
            'dead': 0,
            'hospitalized': 0,
            'critical': 0
        }
        
        for person in self.population.people.values():
            if person.disease_state == DiseaseState.SUSCEPTIBLE:
                stats['susceptible'] += 1
            elif person.disease_state in [DiseaseState.PRESYMPTOMATIC, DiseaseState.ASYMPTOMATIC,
                                        DiseaseState.SYMPTOMATIC_MILD, DiseaseState.SYMPTOMATIC_SEVERE,
                                        DiseaseState.HOSPITALIZED, DiseaseState.CRITICAL]:
                stats['infected'] += 1
                if person.disease_state == DiseaseState.HOSPITALIZED:
                    stats['hospitalized'] += 1
                elif person.disease_state == DiseaseState.CRITICAL:
                    stats['critical'] += 1
            elif person.disease_state in [DiseaseState.RECOVERED_PROTECTED, DiseaseState.RECOVERED_PARTIAL, DiseaseState.RECOVERED_WANED]:
                stats['recovered'] += 1
            elif person.disease_state == DiseaseState.DEAD:
                stats['dead'] += 1
        
        # Record stats
        self.daily_stats['day'].append(self.day)
        for key, value in stats.items():
            self.daily_stats[key].append(value)
        
        # Calculate new infections and deaths
        if self.day == 0:
            self.daily_stats['new_infections'].append(stats['infected'])
            self.daily_stats['new_deaths'].append(0)
        else:
            prev_infected = self.daily_stats['infected'][-1]
            prev_dead = self.daily_stats['dead'][-1]
            self.daily_stats['new_infections'].append(max(0, stats['infected'] - prev_infected))
            self.daily_stats['new_deaths'].append(max(0, stats['dead'] - prev_dead))
    
    def plot_results(self, figsize: Tuple[int, int] = (16, 12)):
        """Plot simulation results using visualizer"""
        self.visualizer.plot_results(figsize)
    
    def _initialize_stats(self):
        """Initialize daily statistics tracking"""
        return {
            'day': [],
            'susceptible': [],
            'infected': [],
            'recovered': [],
            'dead': [],
            'new_infections': [],
            'new_deaths': [],
            'hospitalized': [],
            'critical': []
        }
    
    def _initialize_individual_characteristics(self):
        """Initialize individual characteristics for all agents"""
        # Implementation for setting up individual infectiousness, app usage, etc.
        pass
    
    # Additional methods for disease progression, transmission, interventions, etc.
    # (These would contain the full implementation)