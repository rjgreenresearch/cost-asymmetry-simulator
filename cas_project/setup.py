from setuptools import setup, find_packages
setup(
    name="cost-asymmetry-simulator",
    version="1.1.0",
    author="Robert J. Green",
    author_email="robert@rjgreenresearch.org",
    description="Monte Carlo munitions inventory optimisation — MTS Pillar 3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rjgreenresearch/cost-asymmetry-simulator",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests*"]),
    package_data={"cas": ["../config/*.yaml", "../templates/*.html"]},
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["cas=cas.cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
    ],
)
