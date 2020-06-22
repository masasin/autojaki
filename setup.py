from pathlib import Path
from setuptools import setup


with Path("requirements.txt").open() as requirements:
    DEPENDENCIES = requirements.readlines()


setup(
    name='autojaki',
    version='0.0.1',
    description='Automatically generate and use Jaki codes.',
    license="MIT",
    author='Jean Nassar',
    author_email='jn.masasin@gmail.com',
    url="https://github.com/masasin/autojaki",
    packages=['autojaki'],
    install_requires=DEPENDENCIES,
)
