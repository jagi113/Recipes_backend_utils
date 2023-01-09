# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Scraping recipes',
    version='1.1.0',
    description='Program for scraping recipes, instructions and ingredients from varecha.sk and igredient nutritions from kaloricketabulky.',
    long_description=readme,
    author='Jaroslav Girovsky',
    author_email='jaroslavgirovsky@gmail.com',
    url='https://github.com/jagi113',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))

)
