from setuptools import setup, find_packages

setup(
    name="stockminer",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "futu-api>=6.0.0",
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "stockminer=src.ui.cli:main",
        ],
    },
)
