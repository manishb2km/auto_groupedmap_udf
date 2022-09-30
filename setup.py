from setuptools import setup, find_packages

setup(
    name='autoudf',
    version='0.0.5',
    license='MIT',
    author="Manish Sharma",
    author_email='manishb2km@gmail.com',
    packages=find_packages(include=['autoudf', 'autoudf.*']),
    #package_dir={'': 'src'},
    url='https://github.com/manishb2km/auto_groupedmap_udf',
    keywords='spark automatic schema pandas udf',

)