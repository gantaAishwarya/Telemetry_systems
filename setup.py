from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="telemetry_db",
    version="0.1.0",
    description="Python package to interact with telemetry time-series data on InfluxDB",
    author="Aishwarya Ganta",
    author_email="aishwarya.ganta59@gmail.com",
    packages=find_packages(where="telemetry_db"),
    package_dir={"": "telemetry_db"},
    python_requires=">=3.10",
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
    zip_safe=False,
)
