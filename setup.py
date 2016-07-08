from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

from ricloud import __version__

PACKAGE_NAME = 'ricloud'

install_requires = [
    'requests',

    # Used for sample script, nothing more.
    'unidecode',
]

tests_require = [
    'responses',
    'pytest',
    'pytest-cov',
    'flake8',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['{}/tests/'.format(PACKAGE_NAME)]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

try:
    # This is only important when pushing to PyPi, fine to fail otherwise.
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name=PACKAGE_NAME,
    version=__version__,
    description='Client for Reincubate\'s iCloud API',
    long_description=read_md('README.md'),
    url='https://github.com/reincubate/ricloud',
    author='Ben Emery',
    author_email='ben@reincubate.com',
    license='AGPLv3',
    packages=[PACKAGE_NAME, ],
    package_data={PACKAGE_NAME: ['{}.ini'.format(PACKAGE_NAME), ], },
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    download_url = 'https://github.com/reincubate/{package}/tarball/v{version}'.format(package=PACKAGE_NAME, version=__version__),
    tests_require=tests_require,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Utilities'],
)
