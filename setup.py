from setuptools import setup, find_packages

setup(
    name="pyrobot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'antlr4-python3-runtime==4.13.2',
    ],
) 