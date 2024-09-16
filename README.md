# coastSHARK

[![CI-CD](https://github.com/smartshark/coastSHARK/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/smartshark/coastSHARK/actions/workflows/ci-cd.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://smartshark.github.io/coastSHARK/)

Collect AST Information for smartSHARK.

Currently Java and Python are supported.
For Python the build in [ast](https://docs.python.org/3/library/ast.html) package is used, for java the [javalang](https://github.com/c2nes/javalang) package is used.

## Install

### via PIP
```bash
pip install https://github.com/smartshark/coastSHARK/zipball/master --process-dependency-links
```
The --process-dependency-links switch is needed because we install a modified javalang as a requirement directly from git.

### via setup.py
```bash
python setup.py install
```

## Run Tests
```bash
python setup.py test
```

## Execution for smartSHARK

CoastSHARK needs an already checked out repository. It also depends on a running MongoDB and that the MongoDB is filled for this project by vcsSHARK.
```bash
# after vcsSHARK has run we execute coastSHARK on an already checked out revision $REVISION in a folder $PATH_TO_REPOSITORY
python smartshark_plugin.py -U $DBUSER -P $DBPASS -DB $DBNAME -i $PATH_TO_REPOSITORY -r $REVISION_HASH -u $REPOSITORY_GIT_URI -a $AUTHENTICATION_DB
```

Basically follow the vcsSHARK tutorial and at the end install coastSHARK, checkout the revision to run against in the folder and then execute the above. Parameter for the MongoDB should be the same as with vcsSHARK.

## Python AST extraction

Using the builtin ast package has the advantage of not requiring much code. Although, it has the drawback that it uses the python runtime the coastSHARK is executed with. It is not possible to extract newer python 3.6 nodes if coastSHARK runs on python 3.5 (and the nodes are not present in 3.6, e.g., new keywords). 
There is also the problem with python2 code, at the moment coastSHARK just runs the python code through the lib2to3 package to avoid parsing errors.
A future version of the coastSHARK may mitigate this problem by probing for the version of the python file first. Probably by incrementing the python version for each probe if it catches parsing errors until it can parse the file.

## Java AST extraction

The node types are defined by the javalang package. Other packages for parsing java code and extracting the AST may have different names for the node types.

## Execution Standalone
CoastSHARK can run standalone and write its data to a CSV file for debugging purposes.
```bash
python coastshark.py -i /path/to/folder
```

This creates an ast.csv file in the current folder.