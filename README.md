# coastSHARK
Collect AST Information for smartSHARK.

## Install

### via PIP
```bash
pip install https://github.com/smartshark/coastSHARK/zipball/master --process-dependency-links
```

### via setup.py
```bash
python setup.py install --process-dependency-links
```

## Run Tests
```bash
python setup.py test
```

## Build smartSHARK Plugin .tar
```bash
cd ./plugin_packaging/

# creates the coastSHARK_plugin.tar
./build_plugin.sh
```

## Rebuild schema.json
```bash
cd ./plugin_packaging/

# recreates schema.json from MongoDB models
python build_schema.py
```

## Execution

To run coastSHARK needs an already checked out repository. It also depends on a running MongoDB and that the MongoDB is filled for this project by vcsSHARK.
```bash
python smartshark_plugin.py -U $DBUSER -P $DBPASS -DB $DBNAME -i $PATH_TO_REPOSITORY -r $REVISION_HASH -u $REPOSITORY_GIT_URI
```