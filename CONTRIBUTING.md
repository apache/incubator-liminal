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

## RunningTests

When doing local development and running Liminal unit-tests, make sure to set LIMINAL_STAND_ALONE_MODE=True

1. Setup Minikube
2.Install python requirements: `pip install -r requirements.txt`
3. Run tests: `./run_tests.sh`

## InstallRunPreCommit

[pre-commit](https://pre-commit.com/) is used to install Python code linting and formatting tools:

### Getting started

**Requires `python >=3.6`, `pre-commit>=1.14` and a `git` repository**

1. Run `pip install pre-commit` or `pip install  -r requirements.txt`
2. Install the hooks:
  Simple install without post hooks: `pre-commit install`

  OR
  Install the hooks: `pre-commit install --install-hooks`

  Optional:
  Install the post commit hooks: `pre-commit install --hook-type post-commit`

1. To run pre commit hooks:
   1. Either run `git commit` the new configuration files

   1. Run `pre-commit run -a` to lint and format your entire project

Now on every commit, `pre-commit` will use a git hook to run the tools.
**Warning: the first commit will take some time because the tools are being installed by
`pre-commit`**

`pre-commit run -a` to lint and format your entire project

### Resolving failed commits

* If `black` fail, they have reformatted your code.
* You should check the changes made. Then simply "git add --update ." and re-commit or `git add` and `git commit` the changes.

Example:

![Fixing black failed commits](https://user-images.githubusercontent.com/16241795/146011210-7bc11b24-2033-43f7-8150-5ece4fe7bfea.png)

### EnabledHooks

1. [black](https://black.readthedocs.io/en/stable/): a Python automatic code formatter
1. [yamllint](https://yamllint.readthedocs.io/): A linter for YAML files.
  yamllint does not only check for syntax validity, but for weirdnesses like key repetition and cosmetic problems such as lines length, trailing spaces, indentation, etc.
1. [OutOfBoxHooks](https://github.com/pre-commit/pre-commit-hooks) - Out-of-the-box hooks for pre-commit like Check for files that  contain merge conflict strings
1. [Bandit](https://bandit.readthedocs.io/en/latest/) is a tool designed to find common security issues in Python code.
1. [blacken-docs](https://github.com/asottile/blacken-docs) Run `black` on python code blocks in documentation files
1. [pyupgrade](https://github.com/asottile/pyupgrade) A tool (and pre-commit hook) to automatically upgrade syntax for newer versions of the language.
1. [isort](https://pycqa.github.io/isort/) A Python utility / library to sort imports.
