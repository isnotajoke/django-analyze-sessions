from distutils.core import setup

setup(
    name='django-analyze-sesions',
    version='0.1',
    author='Kevan Carstensen',
    author_email='kevan@isnotajoke.com',
    packages=['analyze_sessions'],
    url='http://isnotajoke.com',
    license='LICENSE.txt',
    description='Tools to analyze Django DB sessions',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.3.0",
    ],
)
