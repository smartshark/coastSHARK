#!/usr/bin/env python

"""This module contains the AST node types and the classes for extracting them from Java and Python.

The most important classes here are ExtractAstPython and ExtractAstJava.
"""

import ast

from lib2to3 import refactor, pgen2

import javalang
from . import error
from .complexity_java import ComplexityJava

# for python
# https://docs.python.org/3/library/ast.html
# node types from: http://greentreesnakes.readthedocs.io/en/latest/nodes.html
PYTHON_NODE_TYPES = ['Num', 'Str', 'Bytes', 'List', 'Tuple', 'Set', 'Dict', 'Ellipsis', 'NameConstant', 'Name', 'Load', 'Store', 'Del', 'Starred', 'Expr', 'UnaryOp', 'UAdd', 'USub', 'Not', 'Invert', 'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult', 'BoolOp', 'And', 'Or', 'Compare', 'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn', 'Call', 'keyword', 'IfExp', 'Attribute', 'Subscript', 'Index', 'Slice', 'ExtSlice', 'ListComp', 'SetComp', 'GeneratorExp', 'DictComp', 'comprehension', 'Assign', 'AugAssign', 'Print', 'Raise', 'Assert', 'Delete', 'Pass', 'Import', 'ImportFrom', 'alias', 'Module', 'Constant', 'FormattedValue', 'JoinedString']

# control flow
PYTHON_NODE_TYPES += ['If', 'For', 'While', 'Break', 'Continue', 'Try', 'TryFinally', 'TryExcept', 'ExceptHandler', 'With', 'withitem']

# function and class defs
PYTHON_NODE_TYPES += ['FunctionDef', 'Lambda', 'arguments', 'arg', 'Return', 'Yield', 'YieldFrom', 'Global', 'Nonlocal', 'ClassDef']

# new async stuff (python 3.5)
PYTHON_NODE_TYPES += ['AsyncFunctionDef', 'Await', 'AsyncFor', 'AsyncWith']

# for java
# node types from: https://github.com/c2nes/javalang/blob/master/javalang/tree.py
JAVA_NODE_TYPES = [
    'CompilationUnit', 'Import', 'Documented', 'Declaration', 'TypeDeclaration', 'PackageDeclaration', 'ClassDeclaration', 'EnumDeclaration', 'InterfaceDeclaration', 'AnnotationDeclaration',
    'Type', 'BasicType', 'ReferenceType', 'TypeArgument',
    'TypeParameter',
    'Annotation', 'ElementValuePair', 'ElementArrayValue',
    'Member', 'MethodDeclaration', 'FieldDeclaration', 'ConstructorDeclaration',
    'ConstantDeclaration', 'ArrayInitializer', 'VariableDeclaration', 'LocalVariableDeclaration', 'FormalParameter', 'InferredFormalParameter',
    'Statement', 'IfStatement', 'WhileStatement', 'DoStatement', 'ForStatement', 'AssertStatement', 'BreakStatement', 'ContinueStatement', 'ReturnStatement', 'ThrowStatement', 'SynchronizedStatement',
    'TryStatement', 'SwitchStatement', 'BlockStatement', 'StatementExpression',
    'TryResource', 'CatchClause', 'CatchClauseParameter',
    'SwitchStatementCase', 'ForControl', 'EnhancedForControl',
    'Expression', 'Assignment', 'TernaryExpression', 'BinaryOperation', 'Cast', 'MethodReference', 'LambdaExpression',
    'Primary', 'Literal', 'This', 'MemberReference', 'Invocation', 'ExplicitConstructorInvocation', 'SuperConstructorInvocation', 'MethodInvocation', 'SuperMethodInvocation', 'SuperMemberReference', 'ArraySelector', 'ClassReference', 'VoidClassReference', 'VariableDeclarator', 'ClassCreator', 'ArrayCreator', 'InnerClassCreator',
    'EnumBody', 'EnumConstantDeclaration', 'AnnotationMethod',
]


# https://docs.python.org/3/library/2to3.html
def convert_2to3(file_content, file_name):
    """Quick helper function to convert python2 to python3 so that we can keep the ast buildin."""

    # all default fixers
    avail_fixes = set(refactor.get_fixers_from_package("lib2to3.fixes"))

    # create default RefactoringTool, apply to passed file_content string and return fixed string
    rt = refactor.RefactoringTool(avail_fixes)
    tmp = rt.refactor_string(file_content, file_name)
    return str(tmp)


class NodePathVisitor(object):
    """Overwrite ast.NodeVisitor because we also want the level for pretty printing.

    This just includes the level for the NodePrintVisitor.
    """

    def visit(self, node, level=0):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, level)

    def generic_visit(self, node, level):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, level=level + 1)
            elif isinstance(value, ast.AST):
                self.visit(value, level=level + 1)


class NodePrintVisitor(NodePathVisitor):
    """Prints AST incl. depth."""

    def generic_visit(self, node, level):
        name = getattr(node, 'id', None)

        if name:
            out = '{} ({})'.format(type(node).__name__, name)
        else:
            out = '{}'.format(type(node).__name__)

        print(' ' * level + out)
        super().generic_visit(node, level)


class NodeTypeCountVisitor(ast.NodeVisitor):
    """Used to count imports, node types and nodes for Python."""

    def __init__(self):
        self.type_counts = {k: 0 for k in PYTHON_NODE_TYPES}  # set 0 for every known type
        self.imports = []
        self.node_count = 0
        super().__init__()

    def generic_visit(self, node):
        type_name = type(node).__name__
        self.node_count += 1
        if type_name in self.type_counts.keys():
            self.type_counts[type_name] += 1
        else:
            # if we encounter an unknown node we have to raise an error because then our vector length is not right
            raise error.CoastException("Unkown NodeType encountered: {}".format(type_name))

        if type_name == 'Import':
            names = getattr(node, 'names', [])
            for n in names:
                self.imports.append(n.name)

        # from datetime import date -> import datetime.date
        if type_name == 'ImportFrom':
            names = getattr(node, 'names', [])
            module = getattr(node, 'module', None)
            for n in names:
                self.imports.append('{}.{}'.format(module, n.name))
        super().generic_visit(node)


class ExtractAstJava(object):
    """Extracts the AST from .java Files.

    Uses the javalang Library.
    """

    def __init__(self, filename):
        self.astdata = None
        self.imports = []
        self.type_counts = {k: 0 for k in JAVA_NODE_TYPES}  # set 0 for every known type
        self.node_count = 0
        self.filename = filename

    def method_metrics(self):
        # new complexity metrics
        cj = ComplexityJava(self.astdata)
        return list(cj.cognitive_complexity())  # we list() here because cognitive_complexity is a generator

    def load(self):
        """Read the AST."""
        try:
            with open(self.filename, 'r', encoding='latin-1') as f:  # latin-1 because we assume no crazy umlaut function names
                self.astdata = javalang.parse.parse(f.read())
        except javalang.parser.JavaSyntaxError as e:
            err = 'Parser Error in file: {}'.format(self.filename)
            raise error.ParserException(err)

        except javalang.tokenizer.LexerError as le:
            err = 'Lexer Error in file: {}\n{}'.format(self.filename, le)
            raise error.ParserException(err)

        assert self.astdata is not None

        for path, node in self.astdata.walk_tree_iterative():
            type_name = type(node).__name__

            self.node_count += 1

            if type_name == 'CompilationUnit':
                for imp in getattr(node, 'imports', []):
                    import_line = imp.path
                    if imp.wildcard:
                        import_line += '.*'
                    self.imports.append(import_line)

            if type_name in self.type_counts.keys():
                self.type_counts[type_name] += 1
            else:
                raise error.CoastException("Unknown NodeType encountered: {}".format(type_name))


class ExtractAstPython(object):
    """Extracts the AST from .py Files.

    Uses the build in ast and the visitor pattern."""

    def __init__(self, filename):
        self.astdata = None
        self.filename = filename

    def load(self):
        """Read the AST.

        We add a \n at the end because 2to3 dies otherwise.
        """
        try:
            with open(self.filename, 'r', encoding='latin-1') as f:
                self.astdata = ast.parse(source=convert_2to3(f.read() + '\n', self.filename), filename=self.filename)

            assert self.astdata is not None

            self.nt = NodeTypeCountVisitor()
            self.nt.visit(self.astdata)
        except pgen2.parse.ParseError as e:
            err = 'Parser Error in file: {}, error: {}'.format(self.filename, e)
            raise error.ParserException(err)
        except SyntaxError as e:
            err = 'Syntax Error in file: {}, error: {}'.format(self.filename, e)
            raise error.SyntaxException(err)

    @property
    def imports(self):
        return self.nt.imports

    @property
    def type_counts(self):
        return self.nt.type_counts

    @property
    def node_count(self):
        return self.nt.node_count
