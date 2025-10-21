#!/bin/bash

# COVID-19 ABM Environment Setup Script

set -e

echo "🚀 Setting up COVID-19 ABM development environment..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install package in development mode
echo "🔨 Installing package in development mode..."
pip install -e .

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results output data/raw simulation_results

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
python -m pytest tests/ -v

echo "✅ Environment setup completed successfully!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the simulation:"
echo "  python examples/basic_simulation.py"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo ""
echo "To build documentation:"
echo "  cd docs && make html"
