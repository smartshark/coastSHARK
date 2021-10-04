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
    if not args.input.endswith('/'):
        raise Exception('--input needs trailing slash')

    # timing
    start = timeit.default_timer()

    log.info("Starting AST extraction")

    m = CsvFile()

    for root, _, files in os.walk(args.input):

        if root.replace(args.input, '') in ignore_dirs:  # subtract base_dir then match against ignore_list
            continue

        for file in files:

            if file in ignore_files:
                continue

            filepath = os.path.join(root, file)
            mongo_filepath = filepath.replace(args.input, '')  # use relative path to find File Document in mongodb

            try:
                if file.endswith('.py'):
                    log.debug('parsing: %s', mongo_filepath)
                    eap = ExtractAstPython(filepath)
                    eap.load()
                    m.write_line(mongo_filepath, eap.imports, eap.node_count, eap.type_counts)

                if file.endswith('.java'):
                    log.debug('parsing: %s', mongo_filepath)
                    eaj = ExtractAstJava(filepath)
                    eaj.load()
                    m.write_line(mongo_filepath, eaj.imports, eaj.node_count, eaj.type_counts)

                    if args.method_metrics:
                        m.write_method_metrics(mongo_filepath, eaj.method_metrics())

            # this is not critical, we can still do the other files
            except error.ParserException as err:
                log.info(str(err))
            # this is critical
            except Exception as err:
                log.error('File: %s', filepath)
                log.exception(err)
                raise

    end = timeit.default_timer() - start
    log.info("Finished AST extraction in {:.5f}s".format(end))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze the given Path.')
    parser.add_argument('-i', '--input', help='Path to the checked out repository directory', required=True)
    parser.add_argument('-mm', '--method_metrics', help='Collect new method metrics (experimental)', default=False)
    main(parser.parse_args())
