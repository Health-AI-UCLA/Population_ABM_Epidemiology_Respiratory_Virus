from setuptools import setup, find_packages

setup(
    name="covid-abm",
    version="1.0.0",
    author="UCLA Health AI",
    description="Agent-based model for respiratory virus epidemiology",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    python_requires=">=3.8",
)
