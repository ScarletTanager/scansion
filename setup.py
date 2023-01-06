from setuptools import setup, find_packages

setup(
    name='scansion',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        meter_details=meter_details:main
    ''',
)