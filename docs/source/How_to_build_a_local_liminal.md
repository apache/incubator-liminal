<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# Building a local installation of Liminal

Start a venv in the liminal example folder
```
python3 -m venv env
```

And activate your virtual environment:
```
source env/bin/activate
```
clean up old versions
```
pip uninstall apache-liminal
```
make sure you have wheel install (should be OK)
```
pip install wheel
```
Set a version for the build:
```
export LIMINAL_BUILD_VERSION=0.0.1.MYVER
```
Build the liminal version in the base of the cloned liminal folder, go to where you cloned it:
```
cd <liminal_path>
git clone https://github.com/apache/incubator-liminal
python3 setup.py sdist bdist_wheel
```

make sure the distribution created is copied to the ./scripts folder
```
cp ./dist/apache_liminal-0.0.1.MYVER-py3-none-any.whl ./scripts
```

local install in target directory
```
cd example_folder
pip install <liminal_path>/scripts/apache_liminal-0.0.1.MYVER-py3-none-any.whl
liminal build
liminal deploy --clean
liminal start
```

How to remove a version and rebuild:
```
cd example_folder
pip uninstall apache-liminal
cd <liminal_path>
rm -r ./dist 
```
