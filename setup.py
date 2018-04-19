import pysplit
from setuptools import setup

setup(
    name='PySplit',
    version=pysplit.__version__,
    packages=['pysplit', 'pysplit.client'],
    scripts=['bin/client.py', 'bin/server.py']
)
