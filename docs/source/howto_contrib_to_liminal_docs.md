<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required bgit y applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# Contributing to Liminal docs

Apache Liminal use Sphinx and readthedocs.org to create and publish documentation to readthedocs.org

## Basic setup
Here is what you need to do in order to work and create docs locally

## Installing sphinx and documentation 

More details  about sphinx and readthedocs can be found [here:](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html)
 
Here is what you need to do:
```
pip install sphinx
```
Inside your project go to docs lib, update the docs you like and build them:
```
cd docs
make html
```

## Automatically rebuild sphinx docs
```
pip install sphinx-autobuild
cd docs
sphinx-autobuild source/ build/html/
```
Now open a browser on 
http://localhost:8000/
Your docs will automatically update

## Rebuilding the pythondoc liminal code documentation
```
cd docs
sphinx-apidoc -o source/ ../liminal
```



