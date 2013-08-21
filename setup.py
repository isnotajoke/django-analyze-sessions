from distutils.core import setup

setup(
    name='django-analyze-sessions',
    version='0.1.1',
    author='Kevan Carstensen',
    author_email='kevan@isnotajoke.com',
    packages=['analyze_sessions', 'analyze_sessions.management', 'analyze_sessions.management.commands'],
    url='https://github.com/isnotajoke/django-analyze-sessions',
    license='MIT',
    description='Tools to analyze Django DB sessions',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.3.0",
    ],
)
