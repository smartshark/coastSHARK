API Documentation
=================

The 2 main modules of *coastSHARK* at the moment are the :any:`extract_ast.py <util.extract_ast>` and :any:`smartshark_plugin.py <smartshark_plugin>`.
The first contains all classes used for AST extraction and the latter contains the code for recursively finding the files in the folder, calling the classes from extract_ast.py and then saving them in the MongoDB.

For saving the information into the MongoDB the :any:`util.write_mongo` module contains a class that wraps the code for the operations on the `pycoshark <https://github.com/smartshark/pycoSHARK>`_ models.

util.extract_ast
----------------

.. automodule:: util.extract_ast
    :members:

util.complexity_java
----------------

.. automodule:: util.complexity_java
    :members:

util.write_mongo
----------------

.. automodule:: util.write_mongo
    :members:

smartshark_plugin
-----------------

.. automodule:: smartshark_plugin
    :members:

    .. autofunction:: main