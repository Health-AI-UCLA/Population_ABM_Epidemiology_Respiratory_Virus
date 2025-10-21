"""
Visualization utilities for model results.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple

class ModelVisualizer:
    """Handle all model visualization needs"""
    
    def __init__(self, model):
        self.model = model
    
    def plot_results(self, figsize: Tuple[int, int] = (16, 12)):
        """Plot comprehensive simulation results"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('COVID-19 ABM Simulation Results', fontsize=16)
        
        # Plot 1: Disease states over time
        ax1 = axes[0, 0]
        ax1.plot(self.model.daily_stats['day'], self.model.daily_stats['susceptible'], 
                label='Susceptible', color='blue')
        ax1.plot(self.model.daily_stats['day'], self.model.daily_stats['infected'], 
                label='Infected', color='red')
        ax1.plot(self.model.daily_stats['day'], self.model.daily_stats['recovered'], 
                label='Recovered', color='green')
        ax1.plot(self.model.daily_stats['day'], self.model.daily_stats['dead'], 
                label='Dead', color='black')
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Number of People')
        ax1.set_title('Disease States Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: New infections and deaths
        ax2 = axes[0, 1]
        ax2.plot(self.model.daily_stats['day'], self.model.daily_stats['new_infections'], 
                label='New Infections', color='orange')
        ax2.plot(self.model.daily_stats['day'], self.model.daily_stats['new_deaths'], 
                label='New Deaths', color='darkred')
        ax2.set_xlabel('Day')
        ax2.set_ylabel('Number of People')
        ax2.set_title('Daily New Cases and Deaths')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Hospital capacity
        ax3 = axes[1, 0]
        ax3.plot(self.model.daily_stats['day'], self.model.daily_stats['hospitalized'], 
                label='Hospitalized', color='purple')
        ax3.plot(self.model.daily_stats['day'], self.model.daily_stats['critical'], 
                label='Critical', color='darkred')
        ax3.set_xlabel('Day')
        ax3.set_ylabel('Number of People')
        ax3.set_title('Hospital Capacity')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Cumulative statistics
        ax4 = axes[1, 1]
        total_infected = [sum(self.model.daily_stats['new_infections'][:i+1]) 
                         for i in range(len(self.model.daily_stats['day']))]
        total_deaths = [sum(self.model.daily_stats['new_deaths'][:i+1]) 
                       for i in range(len(self.model.daily_stats['day']))]
        
        ax4.plot(self.model.daily_stats['day'], total_infected, 
                label='Cumulative Infected', color='red')
        ax4.plot(self.model.daily_stats['day'], total_deaths, 
                label='Cumulative Deaths', color='black')
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Cumulative Number')
        ax4.set_title('Cumulative Cases and Deaths')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_immunity_dynamics(self):
        """Plot detailed immunity dynamics"""
        # Implementation for immunity visualization
        pass
    
    def plot_vaccine_comparison(self, scenarios):
        """Plot comparison of vaccine scenarios"""
        # Implementation for vaccine comparison plots
        pass
