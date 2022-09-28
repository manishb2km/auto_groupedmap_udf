from setuptools import setup, find_packages

setup(
    name='auto_groupedmap_udf',
    version='0.0.1',
    license='MIT',
    author="Manish Sharma",
    author_email='manishb2km@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/manishb2km/auto_groupedmap_udf',
    keywords='spark automatic schema pandas udf',

)