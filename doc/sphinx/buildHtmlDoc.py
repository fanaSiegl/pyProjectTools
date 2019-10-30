#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

os.system('/data/fem/envs/python35_pyqt4/bin/sphinx-build -b html -d build/doctrees source build/html')

print("Build finished.")