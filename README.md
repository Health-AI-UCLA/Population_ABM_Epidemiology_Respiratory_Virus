# COVID-19 Agent-Based Model

[![CI](https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus/workflows/CI/badge.svg)](https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus/actions)
[![Documentation Status](https://readthedocs.org/projects/population-abm-epidemiology/badge/?version=latest)](https://population-abm-epidemiology.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/population-abm-epidemiology.svg)](https://badge.fury.io/py/population-abm-epidemiology)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive epidemiological simulation framework for COVID-19 transmission dynamics, immunity patterns, and intervention effectiveness at population scale.

## 🚀 Features

- **Multi-scale modeling**: 5M+ agents with realistic social networks
- **Enhanced immunity**: Separate reinfection and severe disease protection
- **Dual vaccine types**: Sterilizing and non-sterilizing vaccine scenarios  
- **Comprehensive interventions**: Testing, tracing, quarantine, vaccination
- **Statistical robustness**: 100-run ensemble simulations with confidence intervals
- **Cloud deployment**: Ready for AWS, GCP, Azure with Docker containerization
- **High performance**: Optimized for large-scale simulations with parallel processing

## 📊 Quick Start

```python
from covid_abm import OpenABMCovid19, VaccineParameters

# Create model with vaccination
vaccine_params = VaccineParameters(
    vaccine_type="non_sterilizing",
    vaccination_rate_by_age=[0.01] * 9
)

model = OpenABMCovid19(
    population_size=100000,
    vaccine_params=vaccine_params
)

# Run simulation
results = model.run_simulation(days=365, n_seeds=50)
model.plot_results()
```

## 🛠️ Installation

### From Source
```bash
git clone https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus.git
cd Population_ABM_Epidemiology_Respiratory_Virus
pip install -e .
```

### Using Docker
```bash
docker build -t covid-abm -f docker/Dockerfile .
docker run -v $(pwd)/results:/app/results covid-abm
```

### Development Setup
```bash
./scripts/setup_environment.sh
```

## 📚 Documentation

- **[API Reference](https://population-abm-epidemiology.readthedocs.io/)** - Complete API documentation
- **[Tutorials](docs/notebooks/)** - Interactive Jupyter notebooks
- **[Examples](examples/)** - Ready-to-run simulation scripts
- **[Cloud Deployment](docs/cloud_deployment.md)** - AWS, GCP, Azure setup guides

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=covid_abm --cov-report=html

# Run benchmarks
python scripts/run_benchmarks.py --all
```

## ☁️ Cloud Deployment

### AWS
```bash
python scripts/deploy_to_cloud.py --aws --region us-west-2
```

### Google Cloud Platform
```bash
python scripts/deploy_to_cloud.py --gcp --project-id your-project-id
```

### Azure
```bash
python scripts/deploy_to_cloud.py --azure --resource-group covid-abm-rg
```

## 🔬 Research Applications

This model is designed for epidemiological research and policy analysis:

- **Vaccine effectiveness studies**
- **Intervention strategy evaluation**
- **Herd immunity threshold estimation**
- **Age-stratified risk analysis**
- **Network-based transmission modeling**

## 📈 Performance

- **5M agents**: ~2-4 seconds per simulation day
- **Memory usage**: ~10GB per million agents
- **Scalability**: Tested up to 10M agents
- **Parallel processing**: Multi-core ensemble simulations

## 🤝 Contributing

We welcome contributions from the research community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 Citation

If you use this model in your research, please cite:

```bibtex
@software{covid_abm_2024,
  title = {COVID-19 Agent-Based Model},
  author = {COVID-19 ABM Development Team},
  year = {2024},
  url = {https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus},
  version = {1.0.0}
}
```

## 📋 Requirements

- Python 3.8+
- NumPy, SciPy, Pandas
- Matplotlib, Seaborn
- NetworkX (for network analysis)

## 🔧 Configuration

The model supports extensive parameterization through configuration files:

- **Disease parameters**: Transmission rates, progression probabilities
- **Network parameters**: Social interaction patterns
- **Intervention parameters**: Testing, tracing, quarantine policies
- **Vaccine parameters**: Efficacy, dosing schedules

## 📊 Example Results

The model generates comprehensive epidemiological outputs:

- Daily case counts and hospitalizations
- Age-stratified disease progression
- Network transmission analysis
- Intervention effectiveness metrics
- Statistical confidence intervals

## 🐛 Bug Reports

Found a bug? Please report it using our [issue tracker](https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus/issues).

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenABM-Covid19 community for foundational work
- Epidemiological modeling research community
- Public health agencies for validation data

---

**⚠️ Disclaimer**: This model is for research purposes only and should not be used for clinical decision-making or public health policy without proper validation and expert review.