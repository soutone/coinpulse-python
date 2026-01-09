"""Setup script for coinpulse-python"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="coinpulse",
    version="0.1.0",
    author="CoinPulse",
    author_email="hello@coinpulse.dev",
    description="Simple Python SDK for the CoinPulse crypto portfolio API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soutone/coinpulse-python",
    project_urls={
        "Documentation": "https://coinpulse.dev/docs",
        "Bug Reports": "https://github.com/soutone/coinpulse-python/issues",
        "Source": "https://github.com/soutone/coinpulse-python",
    },
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="crypto cryptocurrency bitcoin ethereum portfolio api sdk",
)
