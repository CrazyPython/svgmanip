import setuptools

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: IronPython",
    "Programming Language :: Python :: Implementation :: Jython",
    "Programming Language :: Python :: Implementation :: MicroPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python :: Implementation :: Stackless",
    "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

KEYWORDS = ["svg", "image", "simple"]

INSTALL_REQUIRES = [
    'svgutils',
    'mpmath',
    'ensure'
]

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='svgmanip',
    version='0.0.10',
    py_modules=['svgmanip'],
    url='https://github.com/CrazyPython/svgmanip',
    license='Apache 2.0',
    author='James Lu',
    author_email='jamtlu@gmail.com',
    description='`svgmanip` helps import and composite together existing SVG drawings. More information is available at the GitHub README.',
    long_description=long_description,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
    packages=setuptools.find_packages(),

)
