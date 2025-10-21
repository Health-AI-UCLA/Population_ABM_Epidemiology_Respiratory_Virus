#!/usr/bin/env python3
"""
Benchmark script for COVID-19 ABM performance testing.
"""

import time
import argparse
import sys
import os
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covid_abm import OpenABMCovid19, DiseaseParameters, NetworkParameters

def benchmark_population_sizes() -> Dict[int, float]:
    """Benchmark different population sizes"""
    print("🔬 Benchmarking population sizes...")
    
    population_sizes = [1000, 5000, 10000, 50000, 100000]
    results = {}
    
    for size in population_sizes:
        print(f"  Testing population size: {size:,}")
        
        # Create model
        model = OpenABMCovid19(population_size=size)
        
        # Time simulation
        start_time = time.time()
        results_data = model.run_simulation(days=30, n_seeds=5, verbose=False)
        end_time = time.time()
        
        duration = end_time - start_time
        results[size] = duration
        
        print(f"    Duration: {duration:.2f} seconds")
        print(f"    People per second: {size/duration:.0f}")
    
    return results

def benchmark_simulation_days() -> Dict[int, float]:
    """Benchmark different simulation durations"""
    print("🔬 Benchmarking simulation durations...")
    
    days = [30, 60, 90, 180, 365]
    results = {}
    population_size = 10000
    
    for day_count in days:
        print(f"  Testing {day_count} days with {population_size:,} people")
        
        # Create model
        model = OpenABMCovid19(population_size=population_size)
        
        # Time simulation
        start_time = time.time()
        results_data = model.run_simulation(days=day_count, n_seeds=5, verbose=False)
        end_time = time.time()
        
        duration = end_time - start_time
        results[day_count] = duration
        
        print(f"    Duration: {duration:.2f} seconds")
        print(f"    Days per second: {day_count/duration:.2f}")
    
    return results

def benchmark_ensemble_runs() -> Dict[int, float]:
    """Benchmark ensemble simulations"""
    print("🔬 Benchmarking ensemble runs...")
    
    n_runs = [1, 5, 10, 20, 50]
    results = {}
    population_size = 5000
    days = 30
    
    for runs in n_runs:
        print(f"  Testing {runs} ensemble runs")
        
        total_time = 0
        for i in range(runs):
            # Create model
            model = OpenABMCovid19(population_size=population_size)
            
            # Time simulation
            start_time = time.time()
            results_data = model.run_simulation(days=days, n_seeds=5, verbose=False)
            end_time = time.time()
            
            total_time += (end_time - start_time)
        
        avg_time = total_time / runs
        results[runs] = avg_time
        
        print(f"    Average duration per run: {avg_time:.2f} seconds")
        print(f"    Total time: {total_time:.2f} seconds")
    
    return results

def print_benchmark_results(results: Dict, title: str):
    """Print benchmark results in a formatted table"""
    print(f"\n📊 {title}")
    print("=" * 50)
    
    if "population" in title.lower():
        print(f"{'Population Size':<15} {'Duration (s)':<12} {'People/sec':<12}")
        print("-" * 50)
        for size, duration in results.items():
            people_per_sec = size / duration
            print(f"{size:<15,} {duration:<12.2f} {people_per_sec:<12.0f}")
    
    elif "duration" in title.lower():
        print(f"{'Days':<8} {'Duration (s)':<12} {'Days/sec':<12}")
        print("-" * 35)
        for days, duration in results.items():
            days_per_sec = days / duration
            print(f"{days:<8} {duration:<12.2f} {days_per_sec:<12.2f}")
    
    elif "ensemble" in title.lower():
        print(f"{'Runs':<8} {'Avg Duration (s)':<15} {'Total Time (s)':<15}")
        print("-" * 40)
        for runs, avg_duration in results.items():
            total_time = avg_duration * runs
            print(f"{runs:<8} {avg_duration:<15.2f} {total_time:<15.2f}")

def main():
    parser = argparse.ArgumentParser(description="COVID-19 ABM Benchmark Suite")
    parser.add_argument("--population", action="store_true", help="Benchmark population sizes")
    parser.add_argument("--duration", action="store_true", help="Benchmark simulation durations")
    parser.add_argument("--ensemble", action="store_true", help="Benchmark ensemble runs")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    
    args = parser.parse_args()
    
    if not any([args.population, args.duration, args.ensemble, args.all]):
        args.all = True
    
    print("🏁 COVID-19 ABM Benchmark Suite")
    print("=" * 50)
    
    if args.all or args.population:
        pop_results = benchmark_population_sizes()
        print_benchmark_results(pop_results, "Population Size Benchmarks")
    
    if args.all or args.duration:
        duration_results = benchmark_simulation_days()
        print_benchmark_results(duration_results, "Simulation Duration Benchmarks")
    
    if args.all or args.ensemble:
        ensemble_results = benchmark_ensemble_runs()
        print_benchmark_results(ensemble_results, "Ensemble Run Benchmarks")
    
    print("\n✅ Benchmarking completed!")

if __name__ == "__main__":
    main()
