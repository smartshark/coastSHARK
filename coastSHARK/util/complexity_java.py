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

SM_DT = {'I': 'int', 'J': 'long', 'V': 'Void', 'Z': 'boolean', 'F': 'float', 'C': 'char', 'B': 'byte', 'D': 'double'}

SM_DT_INV = {v.lower(): k for k, v in SM_DT.items()}


class SourcemeterConversion(object):
    """This is a utility class for matching against Sourcemeter long_names."""

    def __init__(self):
        self._param = re.compile('\(([\w,;,/,\$,\[]*)\)([\w,;,,\./,\$,\[]+)')  # used to map sourcemeter params and return code
        self._log = logging.getLogger('coastSHARK')

    def _remove_bracket(self, dt):
        count = 0
        while dt.startswith('['):
            dt = dt[1:]
            count += 1
        return dt, count

    def get_sm_long_name2(self, long_name):
        """Return a collapsed Sourcemeter long_name."""
        self._long_name = long_name
        m = re.search(self._param, long_name)
        if not m:
            raise Exception('no match found for {}'.format(long_name))

        ret, bc = self._remove_bracket(m.group(2))

        if ret.startswith('L'):
            pruned = self._match_l(ret[1:-1])
            if pruned.lower() in SM_DT_INV.keys():
                ret = '[' * bc + SM_DT_INV[pruned.lower()]
            else:
                ret = '[' * bc + self._match_l('L{};'.format(pruned))

        plist = []
        rest_param = m.group(1)
        while len(rest_param) > 0 and rest_param[0] != ';':
            rest_param, bc = self._remove_bracket(rest_param)
            if rest_param.startswith('L'):
                tmp = rest_param.split(';')
                # reattach the rest
                if len(tmp) > 1:
                    rest_param = ';'.join(tmp[1:]) + ';'  # need to append ; again
                else:
                    rest_param = ''
                # drop L, ; is already dropped
                pruned = self._match_l(tmp[0][1:])
                if pruned.lower() in SM_DT_INV.keys():
                    r = SM_DT_INV[pruned.lower()]
                    plist.append('[' * bc + r)
                else:
                    if pruned:
                        plist.append('[' * bc + 'L{};'.format(pruned))
                    else:
                        plist.append('L')
            else:
                plist.append('[' * bc + rest_param[0])
                rest_param = rest_param[1:]

        start = long_name.split('(')
        return '{}({}){}'.format(start[0], ''.join(plist), ret)

    def get_sm_long_name(self, method):
        """Return a collapsed Sourcemeter long_name from our own method data."""
        ps = []
        for param in method['parameter_types']:
            pruned, bc = self._remove_bracket(param)

            if pruned.lower() in SM_DT_INV.keys():
                ps.append('[' * bc + SM_DT_INV[pruned.lower()])
            else:
                ps.append('[' * bc + 'L{};'.format(pruned))

        if method['return_type'] == 'Void':
            ret = 'V'
        else:
            pruned, bc = self._remove_bracket(method['return_type'])
            if pruned.lower() in SM_DT_INV:
                ret = '[' * bc + SM_DT_INV[pruned.lower()]
            else:
                ret = '[' * bc + 'L{};'.format(pruned)

        params1 = ''.join(ps)
        params2 = ''
        for p in ps:
            if p.lower() == 'j':
                params2 += 'L'
            else:
                params2 += p

        var1 = '{}.{}.{}({}){}'.format(method['package_name'], method['class_name'], method['method_name'], params1, ret)
        var2 = '{}.{}.{}({}){}'.format(method['package_name'], method['class_name'], method['method_name'], params2, ret)
        return var1, var2

    def get_sm_params(self, long_name):
        """Take a Sourcemeter long_name for a method and return a Mapping to our method parameter types and return types.

        This is used to match overloaded functions.
        """
        self._long_name = long_name
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
            rest_param, bc = self._remove_bracket(rest_param)
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

    def _match_l_inner(self, dt, match):
        num_ls = ''
        c = dt.split(match)[0]
        while c.startswith('L'):
            num_ls += 'L'
            c = c[1:]
        return '{}{}'.format(num_ls, dt.split(match)[-1])

    def _match_l(self, dt):
        if '$' in dt:
            return self._match_l_inner(dt, '$')
        elif '.' in dt:
            return self._match_l_inner(dt, '.')
        elif '/' in dt:
            return self._match_l_inner(dt, '/')
        else:
            return dt

    def _match_dt(self, dt):
        dt, bc = self._remove_bracket(dt)
        try:
            r = '[' * bc + SM_DT[dt]
        except KeyError as e:
            self._log.error('[SM MATCH] no such dt key: {} for long_name: {}'.format(dt, self._long_name))
        return r

    def _match_return(self, ret):
        ret, bc = self._remove_bracket(ret)
        if not ret.startswith('L'):
            return '[' * bc + self._match_dt(ret)
        else:
            # get everything between L and ; and return last part
            return '[' * bc + self._match_l(ret[1:-1])


class ComplexityJava(object):
    """Extracts complexity measures from the AST."""

    def __init__(self, compilation_unit_ast):
        """Extract complexity measures from the compilation units AST.

        :param compilation_unit_ast: The AST of the compilation unit (.java file).
        """
        self.ast = compilation_unit_ast
        self._log = logging.getLogger('coastSHARK')

        self._binop = re.compile('binop:"(!?\W+)"')  # used to match operators for sequence changes

    def _method_params(self, method):
        """Extract method parameter and return types, we already do some Sourcmeter notations here, e.g., [ for array."""
        ret_type = 'Void'
        if hasattr(method, 'return_type') and method.return_type:
            r = method.return_type

            # see below
            dim = ''
            if hasattr(r, 'dimensions') and r.dimensions:
                dim = '[' * len(r.dimensions)

            # see below
            while hasattr(r, 'sub_type') and r.sub_type:
                r = r.sub_type

            ret_type = '{}{}'.format(dim, r.name)

        params = []
        for param in method.parameters:
            t = param.type

            # we count dimensions which gives us the array informaiton, e.g., int[] or int[][], we also add this in sourcemeter notation
            dim = ''
            if hasattr(t, 'dimensions') and t.dimensions:
                dim = '[' * len(t.dimensions)

            # method(String... args)
            if param.varargs:
                dim = '['

            # we follow the chain because if we would not do that we would return java instead of ResultSet for java.sql.ResultSet
            while hasattr(t, 'sub_type') and t.sub_type:
                t = t.sub_type

            name = '{}{}'.format(dim, t.name)
            params.append(name)
        return params, ret_type

    def _find_max_level(self):
        """Find maximal level for Counting anonymous Classes.

        A normal ClassDeclaration counts as one level, a ClassCreator counts only if it has inline methods defined.
        """
        max_level = 0
        for path, method in self.ast:

            if type(method).__name__ != 'MethodDeclaration':
                continue

            level = 0
            for i, p in enumerate(path):
                if type(p).__name__ == 'ClassDeclaration':
                    level += 1
                if type(p).__name__ == 'ClassCreator':
                    if 'MethodDeclaration' in [type(n).__name__ for n in path[i + 1]]:
                        level += 1

            if level > max_level:
                max_level = level
        return max_level + 1

    def _class_name(self, path):
        """Return class name in Sourcemeter notation."""
        names = []
        for i, n in enumerate(path):
            class_name = '$'.join(names)
            if type(n).__name__ in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration']:

                # in this case we have a named class inside a method we prepend the counter ala $1NamedClass
                if type(path[i - 2]).__name__ == 'MethodDeclaration':
                    names.append(str(self._count_map[n.position[0]][1]) + n.name)

                # normal named class, just append the name
                else:
                    names.append(n.name)
            elif type(n).__name__ == 'ClassCreator' and self._has_immediate_method(n):
                names.append(str(self._count_map[n.position[0]][0]))
        class_name = '$'.join(names)
        return class_name

    def _has_immediate_method(self, node):
        """Check if the node has a method."""
        for _, n1 in node:
            if type(n1).__name__ == 'MethodDeclaration' and len(_) == 2:
                return True
        return False

    def _parent_pos(self, path):
        """Return parent position for our relevant node types."""
        first = None
        for n in reversed(path):
            if type(n).__name__ not in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration', 'ClassCreator']:
                continue
            if type(n).__name__ in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration']:
                first = n
                break
            if type(n).__name__ == 'ClassCreator' and self._has_immediate_method(n):
                first = n
                break
        return first.position[0]

    def _parse_level_positions(self, ast, max_level=10):
        """Count positions and levels for our relevant node types."""
        for current_level in range(1, max_level):
            for path, node in ast:
                # these do not count towards levels
                if type(node).__name__ not in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration', 'ClassCreator']:
                    continue

                # these count towards the levels
                level = 0
                for i, n in enumerate(path):
                    if type(n).__name__ in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration']:
                        level += 1
                    if type(n).__name__ == 'ClassCreator' and self._has_immediate_method(n):
                        level += 1

                # evaluate the current level
                if level == current_level:

                    # we do only count classCreator nodes with inline methods
                    if type(node).__name__ == 'ClassCreator' and not self._has_immediate_method(node):
                        continue
                    parent_pos = self._parent_pos(path)
                    line = node.position[0]

                    # sadly, we need two lists, one for ClassCreators with methods and another for named classes that are defined inside methods
                    if parent_pos not in self._level_map.keys():
                        self._level_map[parent_pos] = 0

                    if parent_pos not in self._level_map2.keys():
                        self._level_map2[parent_pos] = 0

                    # only count pos for inline classes in methods
                    if type(node).__name__ in ['ClassDeclaration', 'InterfaceDeclaration', 'EnumDeclaration'] and type(path[i - 1]).__name__ == 'MethodDeclaration':
                        self._level_map2[parent_pos] += 1
                    # or inline class creators with methods
                    if type(node).__name__ == 'ClassCreator' and self._has_immediate_method(node):
                        self._level_map[parent_pos] += 1

                    pos1 = self._level_map[parent_pos]
                    pos2 = self._level_map2[parent_pos]
                    self._count_map[line] = (pos1, pos2)

    def cognitive_complexity(self):
        """Extract complexity metrics for all methods of the current file."""
        self._level_map = {}
        self._level_map2 = {}
        self._count_map = {}

        self._parse_level_positions(self.ast, self._find_max_level())

        package = None
        for path, node in self.ast.filter(javalang.tree.PackageDeclaration):
            package = node.name

        for path, method in self.ast:

            # we only are interested in methods and constructors
            if type(method).__name__ not in ['MethodDeclaration', 'ConstructorDeclaration']:
                continue

            full_name = self._class_name(path)

            method_name = method.name
            if type(method).__name__ in 'ConstructorDeclaration':
                method_name = '<init>'  # sourcemeter notation

            self._log.debug('evaluating package {}, class {}, method {}'.format(package, full_name, method_name))

            # gather metrics from the metric ast
            cogcs = self.cognitive_complexity_sonar(method)
            cc = self.cyclomatic_complexity(method)

            params, ret_type = self._method_params(method)

            # we may have interface methods with a body (default methods)
            im = method.body is None
            yield {'package_name': package, 'class_name': full_name, 'method_name': method_name, 'return_type': ret_type, 'parameter_types': params, 'cognitive_complexity_sonar': cogcs, 'cyclomatic_complexity': cc, 'is_interface_method': im}

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
        """Extract cyclomatic complexity (not really, we just count branch types)."""
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

        # 2. use the position of the parent of the BinaryOperation, e.g., if, while as key
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
