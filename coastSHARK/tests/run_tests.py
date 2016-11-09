import unittest
import os

from extract_ast import ExtractAstPython, ExtractAstJava


class TestAstExtraction(unittest.TestCase):

    def test_python(self):
        testfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dummy_test_files/hello.py')

        eap = ExtractAstPython(testfile)
        eap.load()

        node_count = 26
        imports = ['sys', 'os', 'date', 'datetime.date']
        type_counts = {'Load': 5, 'Module': 1, 'Str': 1, 'Expr': 1, 'arguments': 1, 'ImportFrom': 1, 'ClassDef': 1, 'Name': 3, 'arg': 1, 'Attribute': 2, 'FunctionDef': 1, 'alias': 3, 'Call': 3, 'Import': 2}

        self.assertEqual(eap.node_count, node_count)
        self.assertEqual(eap.imports, imports)
        self.assertEqual(eap.type_counts, type_counts)

    def test_java(self):
        testfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dummy_test_files/HelloWorld.java')

        eap = ExtractAstJava(testfile)
        eap.load()

        node_count = 9
        imports = ['javax.awt.*']
        type_counts = {'FormalParameter': 1, 'ReferenceType': 1, 'StatementExpression': 1, 'MethodDeclaration': 1, 'Literal': 1, 'Import': 1, 'MethodInvocation': 1, 'CompilationUnit': 1, 'ClassDeclaration': 1}

        self.assertEqual(eap.node_count, node_count)
        self.assertEqual(eap.imports, imports)
        self.assertEqual(eap.type_counts, type_counts)


if __name__ == '__main__':
    unittest.main()
