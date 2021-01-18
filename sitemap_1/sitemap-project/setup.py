from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='sitemap',
    version='1.0',
    packages=find_packages(),
    long_description=open(
        join(dirname(__file__), 'README.txt')
        ).read(),
    install_requires=[
        'graphviz==0.16',
        'requests==2.22.0',
        'beautifulsoup4==4.9.3'
    ]
)
