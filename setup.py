from setuptools import setup, find_packages

setup(
    name="cost-asymmetry-simulator",
    version="0.1.0",
    description="Compound Warfare Economics Modeling Tool",
    author="Robert J. Green",
    author_email="robert@rjgreenresearch.org",
    url="https://github.com/rjgreenresearch/cost-asymmetry-simulator",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.24.0",
        "networkx>=3.1",
        "matplotlib>=3.7.0",
        "pyyaml>=6.0",
    ],
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
    ],
)
