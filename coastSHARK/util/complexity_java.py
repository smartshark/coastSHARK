#!/usr/bin/env python

"""In this module we extract complexity measures from Java ASTs."""

import logging
import copy
import re

import javalang


JAVA_BRANCH_TYPES = [
    'IfStatement', 'WhileStatement', 'DoStatement', 'ForStatement',
    'SwitchStatement',  # 'SwitchStatementCase',
    'TernaryExpression'  # , 'TryStatement',  cognitive_complexity_sonar does not increment nesting for TryStatement
]

JAVA_NESTING_TYPES = JAVA_BRANCH_TYPES + ['CatchClause']

JAVA_BRANCH_TYPES_MCCC = [
    'IfStatement', 'WhileStatement', 'DoStatement', 'ForStatement',
    'SwitchStatementCase',
    'TernaryExpression'  # , 'TryStatement',  cognitive_complexity_sonar does not increment nesting for TryStatement
]

JAVA_SEQUENCE_TYPES = ['&&', '||']

SM_DT = {'I': 'int', 'J': 'long', 'V': 'Void', 'Z': 'boolean', 'F': 'float', 'C': 'char', 'B': 'byte'}


class SourcemeterConversion(object):

    def __init__(self):
        self._param = re.compile('\(([\w,;,/,\$,\[]*)\)([\w,;,/,\$,\[]+)')  # used to map sourcemeter params and return code
        self._log = logging.getLogger('coastSHARK')

    def get_sm_params(self, long_name):
        """Take a Sourcemeter long_name for a method and return a Mapping to our method parameter types and return types.

        This is used to match overloaded functions.
        """
        m = re.search(self._param, long_name)
        if not m:
            raise Exception('no match found for {}'.format(long_name))
        params = self._match_params(m.group(1))
        ret = self._match_return(m.group(2))

        return params, ret

    def _match_params(self, param):
        plist = []
        rest_param = param
        while len(rest_param) > 0 and rest_param[0] != ';':
            if rest_param.startswith('['):
                rest_param = rest_param[1:]
            if rest_param.startswith('L'):
                tmp = rest_param.split(';')

                # reattach the rest
                if len(tmp) > 1:
                    rest_param = ';'.join(tmp[1:]) + ';'  # need to append ; again
                else:
                    rest_param = ''
                # drop L, ; is already dropped
                plist.append(self._match_l(tmp[0][1:]))
            else:
                plist.append(self._match_dt(rest_param[0]))
                rest_param = rest_param[1:]
        return plist

    def _match_l(self, dt):
        if '$' in dt:
            return dt.split('$')[-1]
        return dt.split('/')[-1]

    def _match_dt(self, dt):
        if '[' in dt:
            dt = dt.replace('[', '')
        return SM_DT[dt]

    def _match_return(self, ret):
        if ret.startswith('['):
            ret = ret[1:]
        if not ret.startswith('L'):
            return self._match_dt(ret)
        else:
            # get everything between L and ; and return last part
            return self._match_l(ret[1:-1])


class ComplexityJava(object):
    """Extracts complextiy measures from the AST."""

    def __init__(self, compilation_unit_ast):
        """Extract complexity measures from the compilation units AST."""
        self.ast = compilation_unit_ast
        self._log = logging.getLogger('coastSHARK')

        self._binop = re.compile('binop:"(!?\W+)"')  # used to match operators for sequence changes

    def _method_params(self, method):
        ret_type = 'Void'
        if hasattr(method, 'return_type') and method.return_type:
            r = method.return_type
            while hasattr(r, 'sub_type') and r.sub_type:
                r = r.sub_type
            ret_type = r.name

        params = []
        for param in method.parameters:
            t = param.type  # we follow the chain because if we would not do that we would return java instead of ResultSet for java.sql.ResultSet
            while hasattr(t, 'sub_type') and t.sub_type:
                t = t.sub_type
            params.append(t.name)
        return params, ret_type

    def _find_max_level(self):
        max_level = 0
        for path, method in self.ast:

            if type(method).__name__ != 'MethodDeclaration':
                continue

            level = 0
            for i, p in enumerate(path):
                if type(p).__name__ == 'ClassCreator' or type(p).__name__ == 'ClassDeclaration':
                    if 'MethodDeclaration' in [type(n).__name__ for n in path[i + 1]]:
                        level += 1

            if level > max_level:
                max_level = level
        return max_level + 1

    def _find_ancestors(self, use_level=1):
        acn = {}
        ac = {}
        for path, method in self.ast:

            if type(method).__name__ != 'MethodDeclaration':
                continue

            level = 0
            for i, p in enumerate(path):
                if type(p).__name__ == 'ClassCreator' or type(p).__name__ == 'ClassDeclaration':
                    if 'MethodDeclaration' in [type(n).__name__ for n in path[i + 1]]:
                        level += 1
                        if level not in ac.keys():
                            ac[level] = {}
                            acn[level] = 0
                        
                        if type(p).__name__ == 'ClassCreator':
                            acn[level] += 1
                            ac[level][p.position[0]] = acn[level]
                        else:
                            ac[level][p.position[0]] = p.name

        if use_level and use_level in ac.keys():
            for pos in sorted(ac[use_level].keys()):
                yield pos, ac[use_level][pos]

    def cognitive_complexity(self):
        """Generate complexity metrics for each method in a declared class (not anonymous classes!)."""
        # first generate order for anonymous functions on nesting level and position in the file
        self.ac = {}
        self.acn = {}

        max_level = self._find_max_level()
        for i in range(1, max_level):
            self.ac[i] = {}
            self.acn[i] = 0
            for pos, line in self._find_ancestors(i):
                if type(line).__name__ == 'int':
                    self.acn[i] += 1
                    self.ac[i][pos] = self.acn[i]
                else:
                    self.ac[i][pos] = line

        package = None
        for path, node in self.ast.filter(javalang.tree.PackageDeclaration):
            package = node.name

        # evaluate interfaces, missing: inner interfaces
        for path, node in self.ast.filter(javalang.tree.InterfaceDeclaration):

            class_name = node.name

            for n in path:
                if type(n).__name__ == 'ClassDeclaration':
                    class_name = '{}${}'.format(n.name, class_name)

            for method in node.methods:
                method_name = method.name
                self._log.debug('evaluating package {}, class {}, method {}'.format(package, class_name, method_name))

                cogcs = self.cognitive_complexity_sonar(method)
                cc = self.cyclomatic_complexity(method)
                params, ret_type = self._method_params(method)
                yield {'package_name': package, 'class_name': class_name, 'method_name': method_name, 'return_type': ret_type, 'parameter_types': params, 'cognitive_complexity_sonar': cogcs, 'cyclomatic_complexity': cc, 'is_interface_method': True}

        # here we only count anonymous methods, we rely on the count in anonymous_classes_
        for path, method in self.ast.filter(javalang.tree.MethodDeclaration):

            # this is kind of a hacky way to do this, basically we discard methods of InterfaceDeclarations
            for n in path:
                if type(n).__name__ == 'InterfaceDeclaration':
                    break
            else:
                ano_name = []
                for i, n in enumerate(path):
                    if type(n).__name__ == 'ClassCreator' or type(n).__name__ == 'ClassDeclaration':
                        if 'MethodDeclaration' in [type(n1).__name__ for n1 in path[i + 1]]:
                            line = n.position[0]
                            for i in range(1, max_level):
                                if line in self.ac[i].keys():
                                    ano_name.append(self.ac[i][line])
                                # print('line: {} in level: {}'.format(line, i))
                if ano_name:
                    # we travel along the path to find the classdeclaration in which we are encountered (we could in theory add the method but Sourcemeter doesnt do it that way)

                    # it may happen that we miss a Class Name in the path because that class does not have other methods
                    for n2 in path:
                        if type(n2).__name__ == 'ClassDeclaration':
                            class_name = n2.name
                            break

                    full_name = '$'.join([str(p) for p in ano_name])

                    # in that case we prepend the name here
                    if not full_name.startswith(class_name):
                        full_name = '{}${}'.format(class_name, full_name)

                    method_name = method.name
                    self._log.debug('evaluating package {}, class {}, method {}'.format(package, full_name, method_name))

                    cogcs = self.cognitive_complexity_sonar(method)
                    cc = self.cyclomatic_complexity(method)
                    params, ret_type = self._method_params(method)
                    yield {'package_name': package, 'class_name': full_name, 'method_name': method_name, 'return_type': ret_type, 'parameter_types': params, 'cognitive_complexity_sonar': cogcs, 'cyclomatic_complexity': cc, 'is_interface_method': False}

        # here we only count declared classes (including nested!)
        for path, node in self.ast.filter(javalang.tree.ClassDeclaration):
            # detect class_name
            class_name = node.name
            # if we encounter a encapsulating class we prepend it (nested class)
            for n in path:
                if type(n).__name__ == 'ClassDeclaration':
                    class_name = '{}${}'.format(n.name, class_name)  # the notation is for better matching sourcemeter

            # strictly not a MethodDeclaration, we may have to change some things
            for method in node.constructors:
                method_name = '<init>'  # the notation is for better matching sourcemeter
                self._log.debug('evaluating package {}, class {}, method {}'.format(package, class_name, method_name))

                cogcs = self.cognitive_complexity_sonar(method)
                cc = self.cyclomatic_complexity(method)
                params, ret_type = self._method_params(method)
                yield {'package_name': package, 'class_name': class_name, 'method_name': method_name, 'return_type': ret_type, 'parameter_types': params, 'cognitive_complexity_sonar': cogcs, 'cyclomatic_complexity': cc, 'is_interface_method': False}

            # normal class methods
            for method in node.methods:
                method_name = method.name
                self._log.debug('evaluating package {}, class {}, method {}'.format(package, class_name, method_name))

                cogcs = self.cognitive_complexity_sonar(method)
                cc = self.cyclomatic_complexity(method)
                params, ret_type = self._method_params(method)
                yield {'package_name': package, 'class_name': class_name, 'method_name': method_name, 'return_type': ret_type, 'parameter_types': params, 'cognitive_complexity_sonar': cogcs, 'cyclomatic_complexity': cc, 'is_interface_method': False}

    def cognitive_complexity_sonar(self, method):
        """Extract cognitive complexity.

        Description here: https://www.sonarsource.com/docs/CognitiveComplexity.pdf
        """
        cogcs = 0
        cogcs += self._nesting(method)
        cogcs += self._binop_cc(method)
        cogcs += self._recursion(method)
        return cogcs

    def cyclomatic_complexity(self, method):
        """Extract cyclomatic complexity."""
        cc = 1
        for c, n in method:
            if type(n).__name__ in JAVA_BRANCH_TYPES_MCCC:
                cc += 1
        return cc

    def _sequence_key(self, path):
        # 1. remove BinaryOperator from path until parent object is reached
        basepath = copy.deepcopy(path)

        while type(basepath[-1]).__name__ in ['BinaryOperation', 'list']:
            basepath = basepath[:-1]
            if type(basepath[-1]).__name__ == 'BinaryOperation' and basepath[-1].operator not in JAVA_SEQUENCE_TYPES:
                basepath = basepath[:-1]
                continue

        # use the position of the parent of the BinaryOperation, e.g., if, while as key
        if not basepath[-1].position:
            raise Exception('no position for: {}'.format(basepath[-1]))
        return basepath[-1].position[0]

    def _recursion(self, method):
        """
        Detect recursion in method.

        This has drawbacks! We will count recursion if we call a method of the same name as the current but with different attributes.
        We do not have the ability to discern attribute types only names and number of attributes.
        """
        cc = 0
        for p, n in method:
            if type(n).__name__ == 'MethodInvocation':
                if n.member == method.name:
                    cc += 1
        return cc

    def _binop_check(self, binop):
        return type(binop).__name__ == 'BinaryOperation' and binop.operator in JAVA_SEQUENCE_TYPES

    def _binop_cc(self, method):
        """Here we look at sequences of binary operations.

        To group them together we first find the position of one binary sequences containing element (if, etc.)
        As we are traversing the tree our first BinaryOperation for a certain containing element will be the middle of all BinaryStatements on the line.
        From there on we traverse the tree and get the sequence in prefix notation.
        We then change to infix notation so that we can count the changes in operators that the human would see and count that.
        """
        tmp = {}
        sequences = {}
        for p, n in method:
            # this hould be the first binop per key
            if self._binop_check(n):
                key = self._sequence_key(p)
                if key not in tmp.keys():
                    tmp[key] = n

        # this appends the nodes to the list in prefix notation
        for k, v in tmp.items():
            sequences[k] = []
            for p, n in v:
                sequences[k].append(n)

        # create infix from prefix notation
        nseq = {}
        for k, v in sequences.items():
            stack = []
            for op in reversed(v):
                if self._binop_check(op):
                    p1 = stack.pop()
                    p2 = stack.pop()
                    p = ''
                    if hasattr(op, 'prefix_operators') and op.prefix_operators:
                        p = '!'
                    stack.append('({} binop:"{}{}" {})'.format(p1, p, op.operator, p2))
                else:
                    stack.append(op)
            nseq[k] = stack.pop()

        # get the human readable sequence of operators and prefix operator (!)
        for k, v in nseq.items():
            tmp = []
            for m in re.findall(self._binop, v):
                if m:
                    tmp.append(m)
            sequences[k] = tmp
            self._log.debug('[seq] found sequence {} at pos {}'.format(tmp, k))

        # count the changes in sequences via the operators, e.g., a && b || c
        full_cc = 0
        for k, v in sequences.items():
            cc = 1
            op = v[0]
            for i, binop in enumerate(v[1:]):
                prefix = None
                if len(binop) > 2:  # we have a prefix
                    prefix = '!'
                    binop = binop[1:]
                if binop != op:
                    cc += 1
                elif prefix:  # binop == op but binop has prefix
                    cc += 1
                op = binop
            full_cc += cc

            self._log.debug('[seq] cc for sequence {} at {} is {}'.format(v, k, cc))
        return full_cc

    def _nesting(self, method):
        cc = 0
        for path, n in method:

            nest = 0  # MethodDeclaration does not count so we can do this here
            for p in path:
                if type(p).__name__ in JAVA_NESTING_TYPES:
                    nest += 1
                    self._log.debug('[nest] {} in {} increase nesting level to {}'.format(p, 'JAVA_NESTING_TYPES', nest))
                if type(p) == [] and type(p[0]).__name__ in JAVA_NESTING_TYPES:
                    nest += 1
                    self._log.debug('[nest] {} in {} increase nesting level to {}'.format(p[0], 'JAVA_NESTING_TYPES', nest))

            nesting = nest
            if type(n).__name__ in JAVA_BRANCH_TYPES + ['TryStatement']:
                cc += 1 + nesting
                self._log.debug('[nest] {} in {} increase cc to {} including nesting {}'.format(n, 'JAVA_BRANCH_TYPES and Try', cc, nesting))
        return cc
