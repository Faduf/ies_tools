#
# Copyright 2016 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup, find_packages

setup(name='ies_tools',
      version='1.0',
      license='Apache-2.0',
      description='Tools for combining and rotating IES-photometric files',
      author='Olli Tapaninen',
      author_email='olli.tapaninen@gmail.com',
      packages=find_packages(),
      entry_points={
          'console_scripts':
          ['combineIES = ies_tools.combineIES:main',
           'rotateIES = ies_tools.rotateIES:main'
           ]
      },
      # This line is only for python setup.py bdist, for PyPI see MANIFEST.in
      requires=['numpy', 'scipy', 'setuptools'],
      include_package_data=False,
      url='http://www.vtt.fi/'
      )
