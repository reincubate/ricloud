import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


PACKAGE_NAME = 'ricloud'


class PyTest(TestCommand):
    """Allows for testing through setuptools. From the pytest docs:
    https://docs.pytest.org/en/latest/goodpractices.html#manual-integration
    """
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = '-n auto'

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def markdown2rst(path):
    try:
        import pypandoc
        return pypandoc.convert(path, 'rst', 'md')
    except ImportError:
        with open(path, 'r') as f:
            return f.read()


setup(
    name=PACKAGE_NAME,

    version='3.0.0rc0',

    description="Python client for Reincubate's ricloud API.",
    long_description=markdown2rst('README.md'),

    url='https://github.com/reincubate/ricloud',

    author='Reincubate',
    author_email='enterprise@reincubate.com',

    license='AGPLv3',

    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        'requests>=2.0; python_version>="3.0"',
        'requests[security]>=2; python_version<"3.0"',
        'click<8.0',
    ],
    tests_require=[
        'pytest>=3.4',
        'pytest-mock>=1.7',
        'pytest-xdist>=1.22',
        'pytest-cov>=2.5',
        'pytest-env>=0.6.2',
    ],
    extras_require={
        'gs': ['google-cloud-storage>=1.13.2,<2'],
        's3': ['boto3>=1.9.79,<2'],
    },

    cmdclass={'test': PyTest},
    entry_points='''
        [console_scripts]
        ricloud=ricloud.cli:cli
    ''',

    packages=[PACKAGE_NAME],
    package_data={PACKAGE_NAME: [PACKAGE_NAME + '/*']},
    include_package_data=True,
    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ],
)
