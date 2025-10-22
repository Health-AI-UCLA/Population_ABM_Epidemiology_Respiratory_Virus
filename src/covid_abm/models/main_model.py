"""
Main COVID-19 agent-based model class.
"""

import math
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

        # Reset severity flags for reinfections
        person.will_be_asymptomatic = False
        person.will_be_mild = False
        person.will_be_hospitalised = False
        person.will_be_critical = False
        person.will_die = False
        person.time_to_hospital = 0
        person.time_to_critical = 0
        person.time_to_death = 0
        person.time_to_recover = 0

        # Severity probabilities informed by age-specific clinical data
        severity_probs = [
            self.disease_params.fraction_asymptomatic[age_group],
            self.disease_params.fraction_mild[age_group],
            self.disease_params.fraction_hospitalised[age_group],
            self.disease_params.fraction_critical[age_group]
        ]

        # Reduce severe outcomes when prior immunity or vaccination is present
        severe_reduction = self._severe_disease_reduction(person)
        severity_probs[2] *= (1.0 - severe_reduction)
        severity_probs[3] *= (1.0 - severe_reduction)

        total = sum(severity_probs)
        if total <= 0:
            severity_probs = [1.0, 0.0, 0.0, 0.0]
        else:
            severity_probs = [p / total for p in severity_probs]

        severity_draw = np.random.choice(
            ['asymptomatic', 'mild', 'hospitalized', 'critical'],
            p=severity_probs
        )

        params = self.disease_params

        # Time to symptoms sampled from gamma distribution
        person.time_to_symptoms = self._sample_time(params.mean_time_to_symptoms, params.sd_time_to_symptoms)

        if severity_draw == 'asymptomatic':
            person.will_be_asymptomatic = True
            person.time_to_recover = self._sample_time(params.mean_asymptomatic_to_recover,
                                                      params.sd_asymptomatic_to_recover)

        elif severity_draw == 'mild':
            person.will_be_mild = True
            recovery_delay = self._sample_time(params.mean_symptom_to_recover_mild,
                                               params.sd_symptom_to_recover_mild)
            person.time_to_recover = person.time_to_symptoms + recovery_delay

        elif severity_draw == 'hospitalized':
            person.will_be_hospitalised = True
            hospital_delay = self._sample_time(params.mean_symptom_to_hospital,
                                               params.sd_symptom_to_hospital)
            person.time_to_hospital = person.time_to_symptoms + hospital_delay
            recovery_delay = self._sample_time(params.mean_hospital_to_recover,
                                               params.sd_hospital_to_recover)
            person.time_to_recover = person.time_to_hospital + recovery_delay

        else:  # critical
            person.will_be_hospitalised = True
            person.will_be_critical = True
            hospital_delay = self._sample_time(params.mean_symptom_to_hospital,
                                               params.sd_symptom_to_hospital)
            person.time_to_hospital = person.time_to_symptoms + hospital_delay
            critical_delay = self._sample_time(params.mean_hospital_to_critical,
                                               params.sd_hospital_to_critical)
            person.time_to_critical = person.time_to_hospital + critical_delay
            recovery_delay = self._sample_time(params.mean_critical_to_recover,
                                               params.sd_critical_to_recover)
            person.time_to_recover = person.time_to_critical + recovery_delay

            fatality_rate = params.fraction_fatality[age_group] * (1.0 - severe_reduction)
            baseline_critical = max(params.fraction_critical[age_group], 1e-6)
            fatality_given_critical = min(1.0, fatality_rate / baseline_critical)
            if fatality_given_critical > 0:
                person.will_die = random.random() < fatality_given_critical
                if person.will_die:
                    death_delay = self._sample_time(params.mean_critical_to_death,
                                                     params.sd_critical_to_death)
                    person.time_to_death = person.time_to_critical + death_delay

        # Ensure recovery occurs after symptom onset
        if person.time_to_recover <= person.time_to_symptoms:
            person.time_to_recover = person.time_to_symptoms + max(1, int(params.mean_symptom_to_recover_mild))
    
    def _update_disease_progression(self):
        """Update disease states for all infected people"""
        for person in self.population.people.values():
            # Release individuals from self-quarantine once the isolation period lapses
            if person.quarantined and person.quarantine_start_day >= 0:
                if self.day - person.quarantine_start_day >= self.intervention_params.self_quarantine_days:
                    person.quarantined = False
                    person.quarantine_start_day = -1

            self._update_vaccine_protection(person)

            if person.disease_state in [DiseaseState.SUSCEPTIBLE, DiseaseState.DEAD]:
                continue

            if person.disease_state in [DiseaseState.RECOVERED_PROTECTED,
                                        DiseaseState.RECOVERED_PARTIAL,
                                        DiseaseState.RECOVERED_WANED]:
                self._update_post_recovery_immunity(person)
                continue

            active_states = {
                DiseaseState.PRESYMPTOMATIC,
                DiseaseState.ASYMPTOMATIC,
                DiseaseState.SYMPTOMATIC_MILD,
                DiseaseState.SYMPTOMATIC_SEVERE,
                DiseaseState.HOSPITALIZED,
                DiseaseState.CRITICAL
            }

            if person.disease_state in active_states:
                person.days_infected += 1

            if person.disease_state == DiseaseState.PRESYMPTOMATIC:
                if person.days_infected >= person.time_to_symptoms:
                    person.symptom_onset_day = self.day
                    if person.will_be_asymptomatic:
                        person.disease_state = DiseaseState.ASYMPTOMATIC
                    elif person.will_be_hospitalised:
                        person.disease_state = DiseaseState.SYMPTOMATIC_SEVERE
                    else:
                        person.disease_state = DiseaseState.SYMPTOMATIC_MILD

            elif person.disease_state == DiseaseState.ASYMPTOMATIC:
                if person.days_infected >= person.time_to_recover:
                    self._transition_to_recovered(person)

            elif person.disease_state == DiseaseState.SYMPTOMATIC_MILD:
                if person.days_infected >= person.time_to_recover:
                    self._transition_to_recovered(person)

            elif person.disease_state == DiseaseState.SYMPTOMATIC_SEVERE:
                if person.will_be_hospitalised and person.days_infected >= person.time_to_hospital:
                    person.disease_state = DiseaseState.HOSPITALIZED
                elif not person.will_be_hospitalised and person.days_infected >= person.time_to_recover:
                    self._transition_to_recovered(person)

            elif person.disease_state == DiseaseState.HOSPITALIZED:
                if person.will_be_critical and person.days_infected >= person.time_to_critical:
                    person.disease_state = DiseaseState.CRITICAL
                elif person.days_infected >= person.time_to_recover:
                    self._transition_to_recovered(person)

            elif person.disease_state == DiseaseState.CRITICAL:
                if person.will_die and person.days_infected >= person.time_to_death:
                    person.disease_state = DiseaseState.DEAD
                elif person.days_infected >= person.time_to_recover:
                    self._transition_to_recovered(person)
    
    def _transmission_step(self):
        """Handle disease transmission"""
        infectious_states = {
            DiseaseState.PRESYMPTOMATIC,
            DiseaseState.ASYMPTOMATIC,
            DiseaseState.SYMPTOMATIC_MILD,
            DiseaseState.SYMPTOMATIC_SEVERE
        }

        base_transmission = self.disease_params.infectious_rate / 1000.0

        for infectious_person in (p for p in self.population.people.values() if p.disease_state in infectious_states):
            contacts_by_type = self._get_contacts(infectious_person)

            days_since_infection = max(0, infectious_person.days_infected)
            profile_index = min(days_since_infection, len(infectious_person.infectious_profile) - 1)
            profile_factor = infectious_person.infectious_profile[profile_index] if infectious_person.infectious_profile else 1.0

            if infectious_person.disease_state == DiseaseState.ASYMPTOMATIC:
                severity_factor = self.disease_params.asymptomatic_infectious_factor
            elif infectious_person.disease_state == DiseaseState.SYMPTOMATIC_MILD:
                severity_factor = self.disease_params.mild_infectious_factor
            else:
                severity_factor = self.disease_params.severe_infectious_factor

            base_prob = base_transmission * profile_factor * infectious_person.individual_infectiousness_factor * severity_factor

            for contact_type, contact_ids in contacts_by_type.items():
                if not contact_ids:
                    continue

                multiplier = getattr(self.network_params, f"relative_transmission_{contact_type}", 1.0)
                for contact_id in contact_ids:
                    if contact_id == infectious_person.id:
                        continue

                    contact = self.population.people[contact_id]
                    if contact.disease_state in infectious_states or contact.disease_state == DiseaseState.DEAD:
                        continue

                    susceptibility = self._compute_susceptibility(contact)
                    if susceptibility <= 0:
                        continue

                    transmission_prob = min(1.0, base_prob * multiplier * susceptibility)

                    if random.random() < transmission_prob:
                        self._infect_person(contact)
                        self.transmission_events.append((self.day, infectious_person.id, contact_id, contact_type))
    
    def _get_contacts(self, person: Person) -> Dict[str, List[int]]:
        """Get daily contacts for a person separated by network layer"""
        contacts: Dict[str, List[int]] = {
            'household': [],
            'occupation': [],
            'random': []
        }

        # Household mixing is assumed daily regardless of quarantine status
        household_contacts = self.population.households.get(person.household_id, [])
        contacts['household'] = [c for c in household_contacts if c != person.id]

        # Symptomatic or quarantined individuals skip workplace/school mixing
        symptomatic_states = {
            DiseaseState.SYMPTOMATIC_MILD,
            DiseaseState.SYMPTOMATIC_SEVERE,
            DiseaseState.HOSPITALIZED,
            DiseaseState.CRITICAL
        }

        attends_occupation = (
            person.occupation_id is not None and
            not person.quarantined and
            person.disease_state not in symptomatic_states and
            random.random() < self.network_params.daily_fraction_work
        )

        if attends_occupation:
            occupation_contacts = [c for c in self.population.occupations.get(person.occupation_id, []) if c != person.id]
            if occupation_contacts:
                target_contacts = self._occupation_contact_count(person.age_group, len(occupation_contacts))
                if target_contacts >= len(occupation_contacts):
                    contacts['occupation'] = occupation_contacts
                else:
                    contacts['occupation'] = random.sample(occupation_contacts, target_contacts)

        # Random/community contacts for mobile individuals
        if not person.quarantined and person.disease_state not in symptomatic_states:
            mean_random = 0.0
            if 0 <= person.age_group < len(self.network_params.mean_random_interactions):
                mean_random = self.network_params.mean_random_interactions[person.age_group]

            n_random = 0
            if mean_random > 0:
                overdispersion = max(1e-3, self.network_params.overdispersion_random)
                p = overdispersion / (overdispersion + mean_random)
                n_random = int(np.random.negative_binomial(overdispersion, p))

            base_contacts = len(contacts['household']) + len(contacts['occupation'])
            if person.daily_interactions_target:
                remaining_capacity = max(0, int(round(person.daily_interactions_target - base_contacts)))
                n_random = min(n_random, remaining_capacity)

            available_people = [p_id for p_id in self.population.people.keys()
                                if p_id != person.id]

            already_contacted = set(contacts['household']) | set(contacts['occupation'])
            available_people = [p_id for p_id in available_people if p_id not in already_contacted]

            if n_random > 0 and available_people:
                contacts['random'] = random.sample(available_people, min(n_random, len(available_people)))

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
        if self.vaccine_params.vaccine_type == "none":
            return

        eligible_states = {
            DiseaseState.SUSCEPTIBLE,
            DiseaseState.RECOVERED_PROTECTED,
            DiseaseState.RECOVERED_PARTIAL,
            DiseaseState.RECOVERED_WANED
        }

        for person in self.population.people.values():
            if person.disease_state not in eligible_states:
                continue

            if not (0 <= person.age_group < len(self.vaccine_params.vaccination_rate_by_age)):
                continue

            daily_rate = max(0.0, self.vaccine_params.vaccination_rate_by_age[person.age_group])
            daily_prob = min(1.0, daily_rate)

            if person.vaccination_doses == 0:
                if random.random() < daily_prob:
                    self._administer_vaccine_dose(person)
            elif person.vaccination_doses == 1 and person.dose1_day >= 0 and person.dose2_day < 0:
                if self.day - person.dose1_day >= self.vaccine_params.dose_interval_days:
                    # Deliver booster when due
                    self._administer_vaccine_dose(person)
    
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
        self._infectious_profile_template = self._build_infectious_profile()

        for person in self.population.people.values():
            # Draw individual infectiousness heterogeneity from a lognormal distribution
            sigma = max(1e-3, self.disease_params.individual_infectiousness_sd)
            person.individual_infectiousness_factor = float(np.random.lognormal(mean=0.0, sigma=sigma))

            # Each person receives a copy of the population-level infectiousness curve
            person.infectious_profile = list(self._infectious_profile_template)

            # Target total daily interactions derived from survey-informed contact means
            if 0 <= person.age_group < len(self.network_params.mean_daily_interactions):
                person.daily_interactions_target = self.network_params.mean_daily_interactions[person.age_group]
            else:
                person.daily_interactions_target = 10
    
    def _build_infectious_profile(self) -> np.ndarray:
        """Create a normalized infectiousness curve using a gamma density"""
        params = self.disease_params
        max_days = max(1, int(math.ceil(params.mean_infectious_period + 3 * params.sd_infectious_period)))
        days = np.arange(max_days, dtype=float) + 1e-3
        shape = max(params.infectiousness_shape, 1e-3)
        scale = max(params.infectiousness_scale, 1e-3)
        profile = (days ** (shape - 1.0)) * np.exp(-days / scale)
        if profile.max() > 0:
            profile /= profile.max()
        else:
            profile = np.ones_like(profile)
        return profile

    def _sample_time(self, mean: float, sd: float) -> int:
        """Draw an integer duration from a gamma distribution"""
        mean = max(mean, 0.1)
        sd = max(sd, 0.1)
        if sd <= 0 or mean <= 0:
            return max(1, int(round(mean)))
        shape = (mean / sd) ** 2
        scale = (sd ** 2) / mean
        return max(1, int(np.random.gamma(shape, scale)))

    def _compute_susceptibility(self, person: Person) -> float:
        """Combine age, prior infection, and vaccination to determine susceptibility"""
        if not (0 <= person.age_group < len(self.disease_params.relative_susceptibility)):
            base = 1.0
        else:
            base = self.disease_params.relative_susceptibility[person.age_group]

        infection_protection = min(1.0, max(0.0, person.infection_protection_level))
        vaccine_protection = min(1.0, max(0.0, person.vaccine_protection_infection))
        combined_protection = 1.0 - (1.0 - infection_protection) * (1.0 - vaccine_protection)
        susceptibility = base * max(0.0, 1.0 - combined_protection)
        return max(0.0, min(1.0, susceptibility))

    def _severe_disease_reduction(self, person: Person) -> float:
        """Return the combined reduction in severe outcomes from immunity and vaccination"""
        vaccine = min(1.0, max(0.0, person.vaccine_protection_severe))
        natural = min(1.0, max(0.0, person.severe_protection_level))
        return max(0.0, min(1.0, 1.0 - (1.0 - vaccine) * (1.0 - natural)))

    def _transition_to_recovered(self, person: Person):
        """Move an individual to the recovered state and refresh immunity trackers"""
        person.disease_state = DiseaseState.RECOVERED_PROTECTED
        person.recovery_day = self.day
        person.days_infected = 0
        person.reinfection_protection_end = self.day + int(self.disease_params.reinfection_protection_days)
        person.infection_protection_level = self.disease_params.reinfection_protection_level
        person.severe_protection_level = 1.0
        person.will_be_asymptomatic = False
        person.will_be_mild = False
        person.will_be_hospitalised = False
        person.will_be_critical = False
        person.will_die = False

    def _update_post_recovery_immunity(self, person: Person):
        """Update waning immunity and recovered state transitions"""
        if person.recovery_day < 0:
            return

        params = self.disease_params
        days_since_recovery = self.day - person.recovery_day

        if days_since_recovery <= params.reinfection_protection_days:
            person.disease_state = DiseaseState.RECOVERED_PROTECTED
            person.infection_protection_level = params.reinfection_protection_level
        elif days_since_recovery <= params.severe_protection_days:
            person.disease_state = DiseaseState.RECOVERED_PARTIAL
            span = max(1.0, params.severe_protection_days - params.reinfection_protection_days)
            waning_fraction = (days_since_recovery - params.reinfection_protection_days) / span
            waning_fraction = min(max(waning_fraction, 0.0), 1.0)
            residual = params.reinfection_protection_level * (1.0 - waning_fraction)
            person.infection_protection_level = max(params.partial_immunity_floor, residual)
        else:
            person.disease_state = DiseaseState.RECOVERED_WANED
            person.infection_protection_level = max(0.0, params.partial_immunity_floor / 2.0)

        severity_decay = math.exp(-params.severe_protection_decay_rate * max(days_since_recovery, 0) /
                                   max(params.severe_protection_days, 1.0))
        if person.disease_state == DiseaseState.RECOVERED_WANED:
            person.severe_protection_level = max(0.0, params.partial_immunity_floor * severity_decay)
        else:
            person.severe_protection_level = max(params.partial_immunity_floor,
                                                 min(1.0, severity_decay))

    def _infect_person(self, person: Person):
        """Apply infection to a susceptible or partially immune person"""
        person.disease_state = DiseaseState.PRESYMPTOMATIC
        person.infection_day = self.day
        person.days_infected = 0
        person.num_infections += 1
        person.recovery_day = -1
        person.reinfection_protection_end = -1
        person.infection_protection_level = 0.0
        person.severe_protection_level = max(0.0, person.severe_protection_level * 0.5)
        person.symptom_onset_day = -1
        person.quarantine_reason = None
        self._set_disease_progression(person)

    def _occupation_contact_count(self, age_group: int, available_contacts: int) -> int:
        """Determine the number of occupation contacts to realise"""
        if available_contacts <= 0:
            return 0

        if age_group == 0:
            mean_contacts = self.network_params.mean_work_interactions_child
        elif age_group == 1:
            mean_contacts = self.network_params.mean_work_interactions_teen
        elif 2 <= age_group <= 5:
            mean_contacts = self.network_params.mean_work_interactions_adult
        else:
            mean_contacts = self.network_params.mean_work_interactions_elderly

        stdev = max(1.0, mean_contacts * 0.3)
        contacts = int(round(random.gauss(mean_contacts, stdev)))
        contacts = max(0, min(contacts, available_contacts))
        return contacts

    def _update_vaccine_protection(self, person: Person):
        """Update vaccine-derived protection accounting for waning"""
        params = self.vaccine_params

        if person.vaccination_doses == 0 or params.vaccine_type == "none":
            person.vaccine_protection_infection = 0.0
            person.vaccine_protection_severe = 0.0
            return

        person.vaccine_type = params.vaccine_type

        if params.vaccine_type == "sterilizing":
            reference_day = person.dose2_day if person.dose2_day >= 0 else person.dose1_day
            if reference_day < 0:
                person.vaccine_protection_infection = 0.0
                person.vaccine_protection_severe = 0.0
                return

            required_delay = params.time_to_protection_dose2 if person.dose2_day >= 0 and reference_day == person.dose2_day \
                else params.time_to_protection_dose1
            days_since = self.day - reference_day

            if days_since < required_delay:
                person.vaccine_protection_infection = 0.0
                person.vaccine_protection_severe = 0.0
                return

            decay = self._vaccine_decay(days_since, params.sterilizing_protection_days,
                                        params.sterilizing_decay_rate)
            efficacy = min(1.0, params.sterilizing_efficacy_infection)
            level = min(1.0, efficacy * decay)
            person.vaccine_protection_infection = level
            person.vaccine_protection_severe = level

        else:  # non-sterilizing vaccine
            base_inf = 0.0
            base_severe = 0.0
            reference_day = -1

            if person.dose1_day >= 0 and self.day - person.dose1_day >= params.time_to_protection_dose1:
                base_inf = params.non_sterilizing_efficacy_infection_dose1
                base_severe = params.non_sterilizing_efficacy_severe_dose1
                reference_day = person.dose1_day

            if person.dose2_day >= 0 and self.day - person.dose2_day >= params.time_to_protection_dose2:
                base_inf = 1.0 - (1.0 - params.non_sterilizing_efficacy_infection_dose1) * \
                    (1.0 - params.non_sterilizing_efficacy_infection_dose2)
                base_severe = 1.0 - (1.0 - params.non_sterilizing_efficacy_severe_dose1) * \
                    (1.0 - params.non_sterilizing_efficacy_severe_dose2)
                reference_day = person.dose2_day

            if reference_day < 0:
                person.vaccine_protection_infection = 0.0
                person.vaccine_protection_severe = 0.0
                return

            days_since = self.day - reference_day
            decay = self._vaccine_decay(days_since, params.non_sterilizing_protection_days,
                                        params.non_sterilizing_decay_rate)
            person.vaccine_protection_infection = min(1.0, base_inf * decay)
            person.vaccine_protection_severe = min(1.0, base_severe * decay)

    def _administer_vaccine_dose(self, person: Person):
        """Give a vaccine dose and immediately update protection"""
        if person.vaccination_doses == 0:
            person.vaccination_doses = 1
            person.dose1_day = self.day
        elif person.vaccination_doses == 1 and person.dose2_day < 0:
            person.vaccination_doses = 2
            person.dose2_day = self.day

        person.vaccine_type = self.vaccine_params.vaccine_type
        self._update_vaccine_protection(person)

    def _vaccine_decay(self, days_since: int, protection_days: float, decay_rate: float) -> float:
        """Exponential-like decay for vaccine protection"""
        if days_since <= 0:
            return 1.0
        if protection_days <= 0:
            return max(0.0, math.exp(-decay_rate * days_since))
        return max(0.0, math.exp(-decay_rate * (days_since / protection_days)))

    # Additional methods for disease progression, transmission, interventions, etc.
    # (These would contain the full implementation)