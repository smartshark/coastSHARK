#!/usr/bin/env python

"""Helper which rewrites schema.json."""

import json
import sys

# we know where we are, we need this for the import below
sys.path.insert(0, '../coastSHARK/')

from util.extract_ast import PYTHON_NODE_TYPES, JAVA_NODE_TYPES


def main():

    java_desc = 'Occurrences of this Java Node Type in the AST of the file, for information on the node types see: https://github.com/c2nes/javalang/blob/master/javalang/tree.py'
    python_desc = 'Occurrences of this Python Node Type in the AST of the file, for information on the node types see: http://greentreesnakes.readthedocs.io/en/latest/nodes.html'
    both_desc = 'Occurrences of this Java and Python Node Type in the AST of the file.'
    node_count_desc = 'Number of AST Nodes in the file.'

    # each AST node type has a field with its number of occurrences in the file
    fields = []
    for nt in PYTHON_NODE_TYPES:
        logical_type = ['ProductMetric', 'ASTNodeType', 'Python']
        desc = python_desc

        # node types that occur in both languages, e.g., import exists in JAVA and PYTHON
        if nt in JAVA_NODE_TYPES:
            logical_type.append('Java')
            desc = both_desc

        fields.append({'type': 'IntegerType', 'logical_type': logical_type, 'field_name': nt, 'desc': desc})

    for nt in JAVA_NODE_TYPES:
        if nt in PYTHON_NODE_TYPES:
            continue  # we already have double nodes

        fields.append({'type': 'IntegerType', 'logical_type': ['ProductMetric', 'ASTNodeType', 'Java'], 'field_name': nt, 'desc': java_desc})

    # we also have tho complete number of nodes
    fields.append({'type': 'IntegerType', 'logical_type': ['ProductMetric', 'ASTNodeType', 'Java', 'Python'], 'field_name': 'node_count', 'desc': node_count_desc})

    schema = {'plugin': 'coastSHARK_1.00',
              'collections': [
                {'collection_name': 'code_entity_state',
                    'fields': [
                        {'field_name': 'imports',
                         'logical_type': ['ProductMetric', 'Java', 'Python'],
                          'sub_type': 'StringType',
                          'type': 'ArrayType',
                          'desc': 'Imports in this file. Extracted from the AST.'},
                        {'field_name': 'metrics',
                         'logical_type': 'Nested',
                         'type': 'StructType',
                         #'desc': 'Metrics',  should already exst
                         'fields': fields}]
                }
              ]}

    with open('schema.json', 'w') as f:
        f.write(json.dumps(schema, sort_keys=True, indent=4))
    print('schema written')


if __name__ == '__main__':
    main()
