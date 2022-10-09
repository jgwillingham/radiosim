#!/usr/bin/env python3
import os
import pathlib
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as build_ext_og

class CMakeExtension(Extension):
	"""
	Extending setuptools' Extension class for running CMake build.
	The `name` argument will be the path to the shared libraries in the
	build directory.
	"""
	def __init__(self, name):
		super().__init__(name, sources=[])

class build_ext(build_ext_og):
	"""
	Extending the build_ext class to run custom CMake build
	"""
	def run(self):
		for ext in self.extensions:
			self.build_cmake(ext)
		super().run()

	def build_cmake(self, ext):
		cwd = pathlib.Path().absolute()

		build_temp = pathlib.Path(self.build_temp)
		build_temp.mkdir(parents=True, exist_ok=True)

		extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
		extdir.mkdir(parents=True, exist_ok=True)

		config = "Debug" if self.debug else 'Release'
		cmake_args = [
			"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + str(extdir.parent.absolute()), 
			"-DCMAKE_BUILD_TYPE=" + config
		]
		build_args = ["--config", config]

		os.chdir(str(build_temp))
		self.spawn(["cmake", str(cwd)] + cmake_args)
		if not self.dry_run:
			self.spawn(["cmake", "--build", "."] + build_args)

		os.chdir(str(cwd))

setup(name = 'radiosim',
	version = '0.0',
	description = 'Wireless communications simulation tool',
	author = 'George Willingham',
	author_email = 'jgwillin@gmail.com',
	url = 'https://github.com/jgwillingham/radiosim',
	packages = find_packages(),
	ext_modules = [CMakeExtension('radiosim.channel.build.lib.channel')],
	cmdclass={
		'build_ext': build_ext,
	}
)
