import pysplit
from setuptools import setup

setup(
    name='PySplit',
    version=pysplit.__version__,
    packages=['pysplit', 'pysplit.client'],
    entry_points={
        'console_scripts': ['pysplit = pysplit.runner:main']
    }
)
