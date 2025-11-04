from setuptools import setup, find_packages  # <- import find_packages

setup(
    name="tanzu_utils",
    version="0.1",
    packages=find_packages(),  # now it works
)