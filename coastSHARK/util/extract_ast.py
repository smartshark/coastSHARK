import ast
import javalang
from . import error

# for python
# https://docs.python.org/3/library/ast.html
# node types from: http://greentreesnakes.readthedocs.io/en/latest/nodes.html

PYTHON_NODE_TYPES = ['Num', 'Str', 'Bytes', 'List', 'Tuple', 'Set', 'Dict', 'Ellipsis', 'NameConstant', 'Name', 'Load', 'Store', 'Del', 'Starred', 'Expr', 'UnaryOp', 'UAdd', 'USub', 'Not', 'Invert', 'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult', 'BoolOp', 'And', 'Or', 'Compare', 'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn', 'Call', 'keyword', 'IfExp', 'Attribute', 'Subscript', 'Index', 'Slice', 'ExtSlice', 'ListComp', 'SetComp', 'GeneratorExp', 'DictComp', 'comprehension', 'Assign', 'AugAssign', 'Print', 'Raise', 'Assert', 'Delete', 'Pass', 'Import', 'ImportFrom', 'alias', 'Module']

# control flow
PYTHON_NODE_TYPES += ['If', 'For', 'While', 'Break', 'Continue', 'Try', 'TryFinally', 'TryExcept', 'ExceptHandler', 'With', 'withitem']

# function and class defs
PYTHON_NODE_TYPES += ['FunctionDef', 'Lambda', 'arguments', 'arg', 'Return', 'Yield', 'YieldFrom', 'Global', 'Nonlocal', 'ClassDef']

# new async stuff
PYTHON_NODE_TYPES += ['AsyncFunctionDef', 'Await', 'AsyncFor', 'AsyncWith']


# for java
# node types from: Zimmermann et al.
JAVA_NODE_TYPES = [
    'AnnotationTypeDeclaration', 'AnnotationTypeMemberDeclaration', 'AnonymousClassDeclaration', 'ArrayAccess', 'ArrayCreation', 'ArrayInitializer', 'ArrayType', 'AssertStatement', 'Assignment', 'Block', 'BlockComment',
    'BooleanLiteral', 'BreakStatement', 'CastExpression', 'CatchClause', 'CharacterLiteral', 'ClassInstanceCreation', 'CompilationUnit', 'ConditionalExpression', 'ConstructorInvocation', 'ContinueStatement', 'DoStatement', 'EmptyStatement',
    'EnhancedForStatement', 'EnumConstantDeclaration', 'EnumDeclaration', 'ExpressionStatement', 'FieldAccess', 'FieldDeclaration', 'ExpressionStatement', 'FieldAccess', 'FieldDeclaration', 'ForStatement', 'IfStatement', 'ImportDeclaration',
    'InfixExpression', 'Initializer', 'InstanceofExpression', 'Javadoc', 'LabeledStatement', 'LineComment', 'MarkerAnnotation', 'MemberRef', 'MemberValuePair', 'MethodDeclaration', 'MethodInvocation', 'MethodRef', 'MethodRefParameter',
    'Modifier', 'NormalAnnotation', 'NullLiteral', 'NumberLiteral', 'PackageDeclaration', 'ParametrizedType', 'ParametrizedExpression', 'PostfixExpression', 'PrefixExpression', 'PrimitiveType', 'QualifiedName', 'QualifiedType',
    'ReturnStatement', 'SimpleName', 'SimpleType', 'SingleMemberAnnotation', 'SingleVariableDeclaration', 'StringLiteral', 'SuperConstructorInvocation', 'SuperFieldAccess', 'SuperMethodInvocation', 'SwitchCase', 'SwitchStatement',
    'SynchronizedStatement', 'TagElement', 'TextElement', 'ThisExpression', 'ThrowStatement', 'TryStatement', 'TypeDeclaration', 'TypeDeclarationStatement', 'TypeLiteral', 'TypeParameter', 'VariableDeclarationExpression',
    'VariableDeclarationFragment', 'VariableDeclarationStatement', 'WhileStatement', 'WildcardType'
]

# for java
# node types from: https://github.com/c2nes/javalang/blob/master/javalang/tree.py
JAVA_NODE_TYPES = [
    'CompilationUnit', 'Import', 'Documented', 'Declaration', 'TypeDeclaration', 'PackageDeclaration', 'ClassDeclaration', 'EnumDeclaration', 'InterfaceDeclaration', 'AnnotationDeclaration',
    'Type', 'BasicType', 'ReferenceType', 'TypeArgument',
    'TypeParameter',
    'Annotation', 'ElementValuePair', 'ElementArrayValue',
    'Member', 'MethodDeclaration', 'FieldDeclaration', 'ConstructorDeclaration',
    'ConstantDeclaration', 'ArrayInitializer', 'VariableDeclaration', 'LocalVariableDeclaration', 'VariableDeclaration', 'FormalParameter', 'InferredFormalParameter',
    'Statement', 'IfStatement', 'WhileStatement', 'DoStatement', 'ForStatement', 'AssertStatement', 'BreakStatement', 'ContinueStatement', 'ReturnStatement', 'ThrowStatement', 'SynchronizedStatement',
    'TryStatement', 'SwitchStatement', 'BlockStatement', 'StatementExpression',
    'TryResource', 'CatchClause', 'CatchClauseParameter',
    'SwitchStatementCase', 'ForControl', 'EnhancedForControl',
    'Expression', 'Assignment', 'TernaryExpression', 'BinaryOperation', 'Cast', 'MethodReference', 'LambdaExpression',
    'Primary', 'Literal', 'This', 'MemberReference', 'Invocation', 'ExplicitConstructorInvocation', 'SuperConstructorInvocation', 'MethodInvocation', 'SuperMethodInvocation', 'ArraySelector', 'ClassReference', 'VoidClassReference',
    'EnumBody', 'EnumConstantDeclaration', 'AnnotationMethod'
]
# newly encountered in checkstyle project
JAVA_NODE_TYPES += ['VariableDeclarator', 'ClassCreator', 'ArrayCreator', 'InnerClassCreator']


class NodePathVisitor(object):
    """
    Overwrite ast.NodeVisitor because we also want the level for pretty printing
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
    """Prints tree incl. path."""

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

    In this case we do everything in this class with the help of
    the javalang Library.
    """

    def __init__(self, filename):
        self.astdata = None
        self.imports = []
        self.type_counts = {k: 0 for k in JAVA_NODE_TYPES}  # set 0 for every known type
        self.node_count = 0
        self.filename = filename

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.astdata = javalang.parse.parse(f.read())
        except javalang.parser.JavaSyntaxError as e:
            err = 'Parser Error in file: {}'.format(self.filename)
            # print(err)
            raise error.ParserException(err)

        except javalang.tokenizer.LexerError as le:
            err = 'Lexer Error in file: {}'.format(self.filename)
            # print(err)
            raise error.ParserException(err)

        assert self.astdata is not None

        for path, node in self.astdata:
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
    """"Extxracts Python ASTs. Uses the build in ast and the visitor pattern."""

    def __init__(self, filename):
        self.astdata = None
        self.filename = filename

    def load(self):
        with open(self.filename, 'r') as f:
            self.astdata = ast.parse(source=f.read(), filename=self.filename)

        assert self.astdata is not None

        self.nt = NodeTypeCountVisitor()
        self.nt.visit(self.astdata)

    @property
    def imports(self):
        return self.nt.imports

    @property
    def type_counts(self):
        return self.nt.type_counts

    @property
    def node_count(self):
        return self.nt.node_count
