#!/usr/bin/env python3
# encoding: utf-8

from distutils.core import setup, Extension

compression_module = Extension('fast_compression', sources=['compression.c'])

setup(name='fast_compression',
      version='0.1.0',
      description='M.C. kids compression/decompression written in C.',
      ext_modules=[compression_module])
