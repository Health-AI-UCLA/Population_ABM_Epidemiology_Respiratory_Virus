"""
Population class for managing agents and network structure.
"""

import random
from typing import Dict, List
from collections import defaultdict
from .person import Person
from .parameters import NetworkParameters

class Population:
    """Population of agents with realistic network structure"""
    
    def __init__(self, size: int, age_distribution: List[float], 
                 household_size_dist: List[float], network_params: NetworkParameters):
        self.size = size
        self.network_params = network_params
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
        
        # Create people with age groups based on distribution
        for age_group, fraction in enumerate(age_distribution):
            n_people = int(self.size * fraction)
            
            for _ in range(n_people):
                if person_id >= self.size:
                    break
                    
                # Create person
                person = Person(person_id, age_group, household_id)
                self.people[person_id] = person
                
                # Add to household
                self.households[household_id].append(person_id)
                
                # Check if household is complete
                household_size = len(self.households[household_id])
                max_household_size = len(household_size_dist)
                
                if household_size >= max_household_size or random.random() < 0.3:
                    household_id += 1
                
                person_id += 1
        
        # Create occupation networks
        self._create_occupation_networks()
    
    def _create_occupation_networks(self):
        """Create age-appropriate occupation networks"""
        occupation_id = 0
        
        # Group people by age for occupation networks
        age_groups = defaultdict(list)
        for person_id, person in self.people.items():
            age_groups[person.age_group].append(person_id)
        
        # Create occupation networks for each age group
        for age_group, people in age_groups.items():
            if age_group <= 1:  # Children (0-19)
                # Schools
                school_size = 20
                for i in range(0, len(people), school_size):
                    school_people = people[i:i+school_size]
                    for person_id in school_people:
                        self.people[person_id].occupation_id = occupation_id
                        self.occupations[occupation_id].append(person_id)
                    occupation_id += 1
                    
            elif age_group <= 5:  # Adults (20-69)
                # Workplaces
                workplace_size = 15
                for i in range(0, len(people), workplace_size):
                    workplace_people = people[i:i+workplace_size]
                    for person_id in workplace_people:
                        self.people[person_id].occupation_id = occupation_id
                        self.occupations[occupation_id].append(person_id)
                    occupation_id += 1
                    
            else:  # Elderly (70+)
                # Social groups
                social_size = 8
                for i in range(0, len(people), social_size):
                    social_people = people[i:i+social_size]
                    for person_id in social_people:
                        self.people[person_id].occupation_id = occupation_id
                        self.occupations[occupation_id].append(person_id)
                    occupation_id += 1
