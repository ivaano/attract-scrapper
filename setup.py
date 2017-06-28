from setuptools import setup, find_packages

setup(
    name='attract_scrapper',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    url='',
    license='GPL',
    author='Ivan Villareal',
    author_email='ivaano@gmail.com',
    description='Scrapper for attract mode frontend',
    install_requires=[
        'Click',
        'requests',
        'py'
    ],
    entry_points='''
        [console_scripts]
        attract_scrapper=scrapper.scrapper:cli
    ''',
)
