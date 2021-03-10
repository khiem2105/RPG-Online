
from distutils.core import setup, Extension

# Variable to store the module 
module = Extension("Cnetwork", sources = ["cnetwork.c"])

setup(name="PackageName",
		version = "1.0",
		description = "This is a package for Cnetwork",
		ext_modules = [module])
