from setuptools import setup, find_packages


import urllib.request

url = "https://raw.githubusercontent.com/d2cml-ai/synthdid.py/main/Readme.md"
response = urllib.request.urlopen(url)
long_description = response.read().decode("utf-8")

setup(
    dependency_links=[],
    install_requires=[
        "numpy>=1.23.5",
        "pandas>=1.5.3",
        "scipy>=1.10.1",
        "matplotlib>=3.7.1",
        "statsmodels>=0.13.5",
    ],
    name="synthdid",
    author="D2CML Team, Alexander Quispe, Rodrigo  Grijalba, Jhon Flores, Franco Caceres",
    version="0.10.1",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="causal-inference",
    url="https://github.com/d2cml-ai/synthdid.py",
    license="MIT",
    description="Synthdid",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering",
    ],
)

