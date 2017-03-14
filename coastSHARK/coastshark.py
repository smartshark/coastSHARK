#!/usr/bin/env python

"""Plugin for execution with serverSHARK."""

import argparse
import os
import sys
import logging
import timeit

from util import error
from util.extract_ast import ExtractAstPython, ExtractAstJava
from util.write_csv import CsvFile

# set up logging, we log everything to stdout except for errors which go to stderr
# this is then picked up by serverSHARK
log = logging.getLogger()
log.setLevel(logging.INFO)
i = logging.StreamHandler(sys.stdout)
e = logging.StreamHandler(sys.stderr)

i.setLevel(logging.INFO)
e.setLevel(logging.ERROR)

log.addHandler(i)
log.addHandler(e)


def main(args):
    # unused for now
    ignore_files = []
    ignore_dirs = []

    # preflight checks
    if not os.path.isdir(args.input):
        raise Exception('--input {} is not valid'.format(args.input))
    if not os.access(args.input, os.R_OK):
        raise Exception('--input {} is not readable'.format(args.input))

    # timing
    start = timeit.default_timer()

    log.info("Starting AST extraction")

    m = CsvFile()

    for root, dirs, files in os.walk(args.input):

        if root.replace(args.input, '') in ignore_dirs:  # subtract base_dir then match against ignore_list
            continue

        for file in files:

            if file in ignore_files:
                continue

            filepath = os.path.join(root, file)
            mongo_filepath = filepath.replace(args.input, '')  # use relative path to find File Document in mongodb

            try:
                if file.endswith('.py'):
                    e = ExtractAstPython(filepath)
                    e.load()
                    m.write_line(mongo_filepath, e.imports, e.node_count, e.type_counts)

                if file.endswith('.java'):
                    e = ExtractAstJava(filepath)
                    e.load()
                    m.write_line(mongo_filepath, e.imports, e.node_count, e.type_counts)

            # this is not critical, we can still do the other files
            except error.ParserException as e:
                log.info(str(e))
                pass
            # this is critical
            except Exception as e:
                log.error('File: {}'.format(filepath))
                log.exception(e)
                raise

    end = timeit.default_timer() - start
    log.info("Finished AST extraction in {:.5f}s".format(end))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze the given Path.')
    parser.add_argument('-i', '--input', help='Path to the checked out repository directory', required=True)
    main(parser.parse_args())
