from os.path import dirname, join
import sys
from setuptools import setup, find_packages


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    import sys

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.python_tag = 'py%i%i' % (sys.version_info.major, sys.version_info.minor)

except ImportError:
    bdist_wheel = None


with open(join(dirname(__file__), 'scrapy_rss/VERSION'), 'rt') as f:
    version = f.read().strip()


with open(join(dirname(__file__), 'requirements.txt'), 'rt') as f:
    install_requires = list(map(str.strip, f))

with open(join(dirname(__file__), 'tests', 'requirements.txt'), 'rt') as f:
    dev_requires = list(map(str.strip, f))

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
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
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
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=install_requires,
        extras_require={
            'testing': dev_requires
        },
        cmdclass={'bdist_wheel': bdist_wheel},
    )
