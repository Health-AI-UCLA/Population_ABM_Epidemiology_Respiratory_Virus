"""
Package setup configuration.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="covid-abm",
    version="1.0.0",
    author="COVID-19 ABM Development Team",
    author_email="covid-abm@example.com",
    description="A comprehensive agent-based model for COVID-19 epidemiological simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Health-AI-UCLA/Population_ABM_Epidemiology_Respiratory_Virus",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "cloud": [
            "boto3>=1.20",
            "google-cloud-storage>=2.0",
            "kubernetes>=18.0",
        ],
        "analysis": [
            "jupyter>=1.0",
            "seaborn>=0.11",
            "plotly>=5.0",
            "dash>=2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "covid-abm=covid_abm.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
