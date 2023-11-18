__version__ = '1.0.0.dev0'

import sys
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 4):
    raise RuntimeError('f2mc8dasm requires Python 3.4 or later')

DESC = "Fujitsu F2MC-8 disassembler"

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Assembly',
    'Topic :: Software Development :: Disassemblers',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: System :: Hardware'
]

setup(
    name='f2mc8dasm',
    version=__version__,
    license='License :: OSI Approved :: BSD License',
    url='https://github.com/mnaberez/f2mc8dasm',
    description=DESC,
    long_description=DESC,
    classifiers=CLASSIFIERS,
    author="Mike Naberezny",
    author_email="mike@naberezny.com",
    maintainer="Mike Naberezny",
    maintainer_email="mike@naberezny.com",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    tests_require=[],
    include_package_data=True,
    zip_safe=False,
    test_suite="f2mc8dasm.tests",
    entry_points={
        'console_scripts': [
            'f2mc8dasm = f2mc8dasm.command:main',
        ],
    },
)
