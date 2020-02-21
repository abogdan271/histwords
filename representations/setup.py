# This is needed to execute to build sparse_io.pyx

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("sparse_io.pyx"))
