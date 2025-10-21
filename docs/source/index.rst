Population ABM Epidemiology Documentation
=========================================

Welcome to the COVID-19 Agent-Based Model (ABM) documentation. This comprehensive epidemiological simulation framework enables modeling of COVID-19 transmission dynamics, immunity patterns, and intervention effectiveness at population scale.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api/index
   tutorials/index
   examples/index
   cloud_deployment
   contributing
   changelog

Features
--------

* **Multi-scale modeling**: 5M+ agents with realistic social networks
* **Enhanced immunity**: Separate reinfection and severe disease protection
* **Dual vaccine types**: Sterilizing and non-sterilizing vaccine scenarios
* **Comprehensive interventions**: Testing, tracing, quarantine, vaccination
* **Statistical robustness**: 100-run ensemble simulations with confidence intervals
* **Cloud deployment**: Ready for AWS, GCP, Azure with Docker containerization

Quick Start
-----------

.. code-block:: python

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

Installation
------------

.. code-block:: bash

   git clone https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus.git
   cd Population_ABM_Epidemiology_Respiratory_Virus
   pip install -e .

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
