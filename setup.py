from setuptools import setup

from ricloud import __version__

PACKAGE_NAME = 'ricloud'


def markdown2rst(path):
    try:
        import pypandoc
        return pypandoc.convert(path, 'rst', 'md')
    except ImportError:
        with open(path, 'r') as f:
            return f.read()


def extract_requirements(path):
    with open(path) as fp:
        return [x.strip() for x in fp.read().split('\n') if not x.startswith('#')]


setup(
    name=PACKAGE_NAME,

    version=__version__,

    description="Python client for Reincubate's ricloud API.",
    long_description=markdown2rst('README.md'),

    url='https://github.com/reincubate/ricloud',

    author='Reincubate',
    author_email='enterprise@reincubate.com',

    license='AGPLv3',

    packages=[PACKAGE_NAME, ],
    package_data={PACKAGE_NAME: [PACKAGE_NAME + '/*']},
    include_package_data=True,

    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Utilities'],

    install_requires=extract_requirements('requirements.txt'),
)
