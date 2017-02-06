Intro
=====

This tool collects AST Information for smartSHARK.
Currently Java and Python are supported. 
For Python the build in `ast <https://docs.python.org/3/library/ast.html>`_ package is used, for java the `javalang <https://github.com/c2nes/javalang>`_ package is used.

This software is supposed to be run as a plugin for serverSHARK. It can be run standalone if a MongoDB is running and vcsSHARK has run beforehand.


.. WARNING:: This software is still in development. Also note some caveats described in :ref:`pyast` and in :ref:`javaast`


Installation
------------


Via PIP
^^^^^^^

.. code-block:: shell-session

    pip install https://github.com/smartshark/coastSHARK/zipball/master --process-dependency-links

.. NOTE:: The --process-dependency-links switch is needed because we install pycoSHARK as a requirement directly from git.


Via setup.py
^^^^^^^^^^^^

.. code-block:: shell-session
    
    python setup.py install


Run tests
---------

.. code-block:: bash
    
    python setup.py test


Execute
-------

To run coastSHARK needs an already checked out repository. It also depends on a running MongoDB and that the MongoDB is filled for this project by `vcsSHARK <https://github.com/smartshark/vcsSHARK>`_.

.. code-block:: bash
    
    python smartshark_plugin.py -U $DBUSER -P $DBPASS -DB $DBNAME -i $PATH_TO_REPOSITORY -r $REVISION_HASH -u $REPOSITORY_GIT_URI -a $AUTHENTICATION_DB


.. _pyast:

Python AST extraction
---------------------

Using the builtin ast package has the advantage of not requiring much code. Although, it has the drawback that it uses the python runtime the coastSHARK is executed with. It is not possible to extract newer python 3.6 nodes if coastSHARK runs on python 3.5 (and the nodes are not present in 3.6, e.g., new keywords). There is also the problem with python2 code, at the moment coastSHARK just runs the python code through the lib2to3 package to avoid parsing errors. A future version of the coastSHARK may mitigate this problem by probing for the version of the python file first. Probably by incrementing the python version for each probe if it catches parsing errors until it can parse the file.


.. _javaast:

Java AST extraction
-------------------

The node types are defined by the javalang package. Other packages for parsing java code and extracting the AST may have different names for the node types.