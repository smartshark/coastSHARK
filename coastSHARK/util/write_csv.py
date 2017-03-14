#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from .extract_ast import PYTHON_NODE_TYPES, JAVA_NODE_TYPES


class CsvFile(object):

    def __init__(self, filename='ast.csv', delimiter=',', quotechar='"'):
        self._filename = filename
        self._fieldnames = list(set(PYTHON_NODE_TYPES + JAVA_NODE_TYPES))  # fieldnames are all known node types

        self._f = open(self._filename, 'w')
        self._csv = csv.DictWriter(self._f, delimiter=delimiter, quotechar=quotechar, fieldnames=['path', 'imports', 'node_count'] + self._fieldnames)
        self._csv.writeheader()

    def write_line(self, path, imports, node_count, type_counts):
        row = {}
        for f in self._fieldnames:
            if f in type_counts.keys():
                row[f] = type_counts[f]
            else:
                row[f] = 0

        row['path'] = path
        row['imports'] = ' '.join(imports)
        row['node_count'] = node_count

        self._csv.writerow(row)
