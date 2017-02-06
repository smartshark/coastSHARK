import unittest
import tempfile

from coastSHARK.util.extract_ast import ExtractAstPython, ExtractAstJava
from coastSHARK.util.extract_ast import PYTHON_NODE_TYPES, JAVA_NODE_TYPES


PYTHON_TEST_FILE_CONTENT = """
import sys
import os
from datetime import date

class HelloWorld(object):

    def hello(self):
        print("Hello World on {}".format(date.today()))
"""

PYTHON2_TEST_FILE_CONTENT = """
import sys
import urlparse

url = urlparse.urlparse('http://www.uni-goettingen.de')
print "narf: %s" % ("narf2",)
"""

JAVA_TEST_FILE_CONTENT = """
import javax.awt.*;

public class HelloWorld {

    public static void main(Sting[] args) {
        System.out.println("Hello World!");
    }
}
"""


class TestAstExtraction(unittest.TestCase):
    """Just some very basic Tests for AST extraction code."""

    def test_python(self):

        py = tempfile.NamedTemporaryFile(delete=False)
        py.write(PYTHON_TEST_FILE_CONTENT.encode('utf-8'))
        py.close()

        eap = ExtractAstPython(py.name)
        eap.load()

        node_count = 26
        imports = ['sys', 'os', 'datetime.date']
        wanted_type_counts = {'Load': 5, 'Module': 1, 'Str': 1, 'Expr': 1, 'arguments': 1, 'ImportFrom': 1, 'ClassDef': 1, 'Name': 3, 'arg': 1, 'Attribute': 2, 'FunctionDef': 1, 'alias': 3, 'Call': 3, 'Import': 2}

        type_counts = {k: 0 for k in PYTHON_NODE_TYPES}
        for k, v in wanted_type_counts.items():
            type_counts[k] = v

        self.assertEqual(eap.node_count, node_count)
        self.assertEqual(eap.imports, imports)
        self.assertEqual(eap.type_counts, type_counts)

    def test_python2(self):

        py = tempfile.NamedTemporaryFile(delete=False)
        py.write(PYTHON2_TEST_FILE_CONTENT.encode('utf-8'))
        py.close()

        eap = ExtractAstPython(py.name)
        eap.load()

        node_count = 26
        imports = ['sys', 'urllib.parse']  # urlparse => urllib.parse
        wanted_type_counts = {'Store': 1, 'Attribute': 2, 'Assign': 1, 'Load': 5, 'Str': 3, 'Module': 1, 'Call': 2, 'Name': 3, 'Tuple': 1, 'BinOp': 1, 'Expr': 1, 'Import': 2, 'Mod': 1, 'alias': 2}

        type_counts = {k: 0 for k in PYTHON_NODE_TYPES}
        for k, v in wanted_type_counts.items():
            type_counts[k] = v

        self.assertEqual(eap.node_count, node_count)
        self.assertEqual(eap.imports, imports)
        self.assertEqual(eap.type_counts, type_counts)

    def test_java(self):
        java = tempfile.NamedTemporaryFile(delete=False)
        java.write(JAVA_TEST_FILE_CONTENT.encode('utf-8'))
        java.close()

        eap = ExtractAstJava(java.name)
        eap.load()

        node_count = 9
        imports = ['javax.awt.*']
        wanted_type_counts = {'FormalParameter': 1, 'ReferenceType': 1, 'StatementExpression': 1, 'MethodDeclaration': 1, 'Literal': 1, 'Import': 1, 'MethodInvocation': 1, 'CompilationUnit': 1, 'ClassDeclaration': 1}

        type_counts = {k: 0 for k in JAVA_NODE_TYPES}
        for k, v in wanted_type_counts.items():
            type_counts[k] = v

        self.assertEqual(eap.node_count, node_count)
        self.assertEqual(eap.imports, imports)
        self.assertEqual(eap.type_counts, type_counts)


if __name__ == '__main__':
    unittest.main()
