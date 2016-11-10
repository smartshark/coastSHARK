#!/usr/bin/env python

"""Rewrites schema.json according to the MongoDB Models and our special types we defined."""

# we know where we are
import sys
sys.path.insert(0, '../coastSHARK/')

import json
from mongoengine import ObjectIdField, ListField, DictField, IntField

from util.mongomodels import Import, NodeTypeCount
from util.extract_ast import PYTHON_NODE_TYPES, JAVA_NODE_TYPES


def mongo_to_schema(field_name, field):
        if type(field) == ObjectIdField:
            # exception for id
            if field_name == 'id':
                field_name = '_id'
            return {'type': 'StringType', 'logical_type': 'ID', 'field_name': field_name}
        elif type(field) == ListField:
            return {'type': 'ArrayType', 'logical_type': 'ProductMetric', 'field_name': field_name}
        elif type(field) == DictField:
            return {'type': 'StructType', 'logical_type': 'ProductMetric', 'field_name': field_name}
        elif type(field) == IntField:
            return {'type': 'IntegerType', 'logical_type': 'ProductMetric', 'field_name': field_name}


def main():
    schema = {'plugin': 'coastSHARK_1.00',
              'collections': []}
    fields = []
    for k, v in Import._fields.items():
        field = mongo_to_schema(k, v)

        if k == 'imports':
            field['sub_type'] = 'StringType'
        fields.append(field)

    schema['collections'].append({'collection_name': 'import', 'fields': fields})

    fields = []
    for k, v in NodeTypeCount._fields.items():
        field = mongo_to_schema(k, v)

        # we need to add every possible ast node type
        if k == 'nodeTypeCounts':
            sfields = []
            for nt in PYTHON_NODE_TYPES + JAVA_NODE_TYPES:
                sfields.append({'type': 'IntegerType', 'logical_type': 'ProductMetric', 'field_name': nt})
            field['fields'] = sfields

        fields.append(field)

    schema['collections'].append({'collection_name': 'node_type_count', 'fields': fields})

    with open('schema.json', 'w') as f:
        f.write(json.dumps(schema, sort_keys=True, indent=4))
    # print(json.dumps(schema))
    print('schema written')


if __name__ == '__main__':
    main()
