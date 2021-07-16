from setuptools import setup, find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('libmdwiki/data/')

VERSION = '0.0.1'
DESCRIPTION = 'Static wiki from markdown files'

setup(
        name = 'mdwiki',
        version=VERSION,
        author='Grzegorz Dudziński',
        author_email="<g.p.dudzinski@gmail.com>",
        description=DESCRIPTION,
        packages=find_packages(),
        url='https://github.com/perkun/mdwiki.git',
        install_requires=['jinja2', 'markdown'],
        keywords=['python', 'wiki', 'markdown'],
        classifiers= [
            "Development Status :: 1 - Alpha",
            "Intended Audience :: All",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Unix"
        ],
        scripts=['bin/mdwiki'],
        include_package_data=True,
        package_data={'': extra_files},
)
