from os.path import dirname, join
import sys
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'scrapy_rss/VERSION'), 'rt') as f:
    version = f.read().strip()

with open('README.rst') as readme:
    setup(
        name='scrapy-rss',
        version=version,
        url='https://github.com/woxcab/scrapy_rss',
        description='RSS Tools for Scrapy Framework',
        long_description=readme.read(),
        license='BSD',
        packages=find_packages(exclude=('tests',)),
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            'Framework :: Scrapy',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=['python-dateutil',
                          'scrapy>=1.1' if sys.version_info < (3, 6) else 'scrapy>=1.3.1',
                          'six'],
    )
