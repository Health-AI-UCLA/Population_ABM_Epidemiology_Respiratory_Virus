"""
Population class for managing agents and network structure.
"""

import random
from typing import Dict, List
from collections import defaultdict

import numpy as np
from .person import Person
from .parameters import NetworkParameters

class Population:
    """Population of agents with realistic network structure"""
    
    def __init__(self, size: int, age_distribution: List[float],
                 household_size_dist: List[float], network_params: NetworkParameters):
        self.size = size
        self.network_params = network_params
        self.age_distribution = list(age_distribution)
        self.people: Dict[int, Person] = {}
        self.households: Dict[int, List[int]] = defaultdict(list)
        self.occupations: Dict[int, List[int]] = defaultdict(list)
        
        # Generate reference households for realistic age mixing
        self.reference_households = self._generate_reference_households()
        
        # Create population
        self._create_population(age_distribution, household_size_dist)
    
    def _generate_reference_households(self) -> List[List[int]]:
        """Generate reference households with realistic age distributions"""
        reference = []
        
        # Single person households (mostly elderly)
        for _ in range(100):
            age = random.choice([6, 7, 8])
            reference.append([age])
        
        # Couples (no children)
        for _ in range(150):
            ages = [random.randint(3, 7), random.randint(3, 7)]
            reference.append(ages)
            
        # Families with children
        for _ in range(200):
            n_children = random.randint(1, 3)
            children = [random.randint(0, 1) for _ in range(n_children)]
            parents = [random.randint(3, 5), random.randint(3, 5)]
            reference.append(children + parents)
            
        # Multi-generational households
        for _ in range(50):
            children = [random.randint(0, 1)]
            parents = [random.randint(3, 5), random.randint(3, 5)]
            grandparents = [random.randint(6, 7)]
            reference.append(children + parents + grandparents)
            
        return reference

    def _create_population(self, age_distribution: List[float], household_size_dist: List[float]):
        """Create population with realistic household and occupation structure"""
        person_id = 0
        household_id = 0

        # Normalize distributions
        age_distribution = np.array(age_distribution, dtype=float)
        if age_distribution.sum() <= 0:
            age_distribution = np.ones_like(age_distribution) / len(age_distribution)
        else:
            age_distribution = age_distribution / age_distribution.sum()

        household_weights = np.array(household_size_dist, dtype=float)
        if household_weights.sum() <= 0:
            household_weights = np.ones_like(household_weights) / len(household_weights)
        else:
            household_weights = household_weights / household_weights.sum()

        remaining_age_counts = list(np.random.multinomial(self.size, age_distribution))

        while sum(remaining_age_counts) > 0 and person_id < self.size:
            remaining_people = self.size - person_id
            household_size = self._sample_household_size(household_weights, remaining_people)
            household_size = min(household_size, sum(remaining_age_counts))

            template = self._sample_household_template(household_size)

            household_age_groups: List[int] = []
            for desired_age in template:
                if len(household_age_groups) >= household_size:
                    break
                if sum(remaining_age_counts) <= 0:
                    break
                age_group = self._select_age_group(desired_age, remaining_age_counts)
                household_age_groups.append(age_group)

            while len(household_age_groups) < household_size and sum(remaining_age_counts) > 0:
                fallback_age = self._select_age_group(random.randrange(len(remaining_age_counts)), remaining_age_counts)
                household_age_groups.append(fallback_age)

            if not household_age_groups:
                break

            for age_group in household_age_groups:
                if person_id >= self.size:
                    break

                person = Person(person_id, age_group, household_id)
                self.people[person_id] = person
                self.households[household_id].append(person_id)
                person_id += 1

            if self.households[household_id]:
                household_id += 1

        # Create occupation networks
        self._create_occupation_networks()

    def _sample_household_size(self, size_weights: np.ndarray, remaining_people: int) -> int:
        """Sample a household size constrained by remaining people"""
        size_options = np.arange(1, len(size_weights) + 1)
        valid = size_options <= max(1, remaining_people)
        if not valid.any():
            return max(1, min(remaining_people, 1))
        size_choices = size_options[valid]
        weights = size_weights[valid]
        if weights.sum() <= 0:
            weights = np.ones_like(size_choices) / len(size_choices)
        else:
            weights = weights / weights.sum()
        return int(np.random.choice(size_choices, p=weights))

    def _sample_household_template(self, size: int) -> List[int]:
        """Select an age-structured household template"""
        candidates = [template for template in self.reference_households if len(template) == size]
        if candidates:
            return list(random.choice(candidates))

        weights = np.array(self.age_distribution, dtype=float)
        if weights.sum() <= 0:
            weights = np.ones(len(self.age_distribution)) / len(self.age_distribution)
        else:
            weights = weights / weights.sum()
        choices = np.random.choice(np.arange(len(self.age_distribution)), size=size, p=weights)
        return list(int(x) for x in choices)

    def _select_age_group(self, preferred_age: int, remaining_counts: List[int]) -> int:
        """Choose an age group close to the preferred template while respecting remaining counts"""
        if 0 <= preferred_age < len(remaining_counts) and remaining_counts[preferred_age] > 0:
            remaining_counts[preferred_age] -= 1
            return preferred_age

        for offset in range(1, len(remaining_counts)):
            lower = preferred_age - offset
            if 0 <= lower < len(remaining_counts) and remaining_counts[lower] > 0:
                remaining_counts[lower] -= 1
                return lower
            upper = preferred_age + offset
            if 0 <= upper < len(remaining_counts) and remaining_counts[upper] > 0:
                remaining_counts[upper] -= 1
                return upper

        for idx, count in enumerate(remaining_counts):
            if count > 0:
                remaining_counts[idx] -= 1
                return idx

        return max(0, preferred_age) % len(remaining_counts)
    
    def _create_occupation_networks(self):
        """Create age-appropriate occupation networks"""
        occupation_id = 0

        children = [pid for pid, person in self.people.items() if person.age_group == 0]
        teens = [pid for pid, person in self.people.items() if person.age_group == 1]
        adults = [pid for pid, person in self.people.items() if 2 <= person.age_group <= 5]
        elderly = [pid for pid, person in self.people.items() if person.age_group >= 6]

        random.shuffle(children)
        random.shuffle(teens)
        random.shuffle(adults)
        random.shuffle(elderly)

        remaining_adults = list(adults)

        def assign_group(member_ids: List[int], mean_contacts: float, minimum_size: int,
                         adult_ratio: float = 0.0):
            nonlocal occupation_id, remaining_adults
            idx = 0
            while idx < len(member_ids):
                remaining = len(member_ids) - idx
                group_size = self._draw_group_size(mean_contacts, remaining, minimum_size)
                group = member_ids[idx:idx + group_size]
                idx += group_size

                staff = []
                if adult_ratio > 0 and remaining_adults:
                    staff_needed = int(round(len(group) * adult_ratio))
                    staff_needed = min(staff_needed, len(remaining_adults))
                    for _ in range(staff_needed):
                        staff.append(remaining_adults.pop())

                full_group = group + staff
                for pid in full_group:
                    self.people[pid].occupation_id = occupation_id
                    self.occupations[occupation_id].append(pid)
                occupation_id += 1

        assign_group(children, self.network_params.mean_work_interactions_child, minimum_size=5,
                     adult_ratio=self.network_params.child_network_adults_ratio)
        assign_group(teens, self.network_params.mean_work_interactions_teen, minimum_size=5,
                     adult_ratio=self.network_params.child_network_adults_ratio / 2.0)

        # Remaining adults (excluding those deployed as staff) are assigned to workplaces
        assign_group(remaining_adults, self.network_params.mean_work_interactions_adult, minimum_size=3)

        # Elderly social groups may include adult caregivers
        assign_group(elderly, self.network_params.mean_work_interactions_elderly, minimum_size=2,
                     adult_ratio=self.network_params.elderly_network_adults_ratio)

    def _draw_group_size(self, mean_contacts: float, remaining: int, minimum_size: int) -> int:
        """Draw a group size so that average contacts align with survey estimates"""
        base_size = max(minimum_size, int(round(mean_contacts)) + 1)
        stdev = max(1.0, base_size * 0.25)
        sampled = int(round(random.gauss(base_size, stdev)))
        sampled = max(minimum_size, sampled)
        sampled = min(sampled, remaining)
        return max(minimum_size, sampled)
