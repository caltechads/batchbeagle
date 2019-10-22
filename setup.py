#!/usr/bin/env python
from batchbeagle import __version__
from setuptools import setup, find_packages

# intro = open('docs/source/intro.rst').read()

setup(name="batchbeagle",
      version=__version__,
      description="AWS Batch related deployment tools",
      author="Caltech IMSS ADS",
      author_email="imss-ads-staff@caltech.edu",
      url="https://github.com/caltechads/batchbeagle",
      # long_description=intro,
      keywords=['aws', 'batch'],
      classifiers = [
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3"
      ],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          "boto3 >= 1.4.4",
          "click >= 6.7",
          "PyYAML == 5.1"
      ],
      entry_points={'console_scripts': [
          'beagle = batchbeagle.dplycli:main'
      ]}
      )
