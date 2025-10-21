#!/bin/bash

# COVID-19 ABM Docker Entrypoint Script

set -e

echo "Starting COVID-19 ABM simulation..."

# Check if we have the required environment variables
if [ -z "$POPULATION_SIZE" ]; then
    export POPULATION_SIZE=100000
fi

if [ -z "$SIMULATION_DAYS" ]; then
    export SIMULATION_DAYS=365
fi

if [ -z "$N_SEEDS" ]; then
    export N_SEEDS=10
fi

echo "Configuration:"
echo "  Population size: $POPULATION_SIZE"
echo "  Simulation days: $SIMULATION_DAYS"
echo "  Number of seeds: $N_SEEDS"

# Create results directory if it doesn't exist
mkdir -p /app/results

# Run the simulation
if [ "$1" = "ensemble" ]; then
    echo "Running ensemble simulation..."
    python scripts/run_ensemble.py \
        --population-size $POPULATION_SIZE \
        --days $SIMULATION_DAYS \
        --n-seeds $N_SEEDS \
        --n-runs ${N_RUNS:-100}
elif [ "$1" = "jupyter" ]; then
    echo "Starting Jupyter notebook server..."
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
else
    echo "Running basic simulation..."
    python examples/basic_simulation.py
fi

echo "Simulation completed!"
