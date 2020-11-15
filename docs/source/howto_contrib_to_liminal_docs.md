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


