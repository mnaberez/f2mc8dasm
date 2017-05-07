__version__ = '1.0.0-dev'

from setuptools import setup, find_packages

DESC = ""

CLASSIFIERS = []

setup(
    name='f2mc8dasm',
    version=__version__,
    license='License :: OSI Approved :: BSD License',
    url='',
    description='',
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
