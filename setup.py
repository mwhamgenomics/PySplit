import pysplit
from setuptools import setup

setup(
    name='PySplit',
    version=pysplit.__version__,
    packages=['pysplit', 'pysplit.client'],
    install_requires=['requests>=2.20.0', 'PyYAML>=5.3.1',
                      'Flask>=1.1.2', 'tornado>=5.1', 'playsound>=1.2'],
    entry_points={
        'console_scripts': ['pysplit = pysplit.runner:main']
    }
)
