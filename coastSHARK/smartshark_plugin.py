#!/usr/bin/env python

"""Plugin for smartSHARK"""

import argparse
import os
import sys
import logging
import timeit

from util import error
from util.extract_ast import ExtractAstPython, ExtractAstJava
from util.write_mongo import MongoDb

# set up logging
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

    # check mongodb connectivity
    m = MongoDb(args.db_hostname, args.db_port, args.db_database, args.db_user, args.db_password, args.db_authentication, args.url, args.rev)
    m.connect()

    log.info("Starting AST Extraction")

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
                    m.write_imports(mongo_filepath, e.imports)
                    m.write_node_type_counts(mongo_filepath, e.node_count, e.type_counts)

                if file.endswith('.java'):
                    e = ExtractAstJava(filepath)
                    e.load()
                    m.write_imports(mongo_filepath, e.imports)
                    m.write_node_type_counts(mongo_filepath, e.node_count, e.type_counts)
            # this is not critical, we can still do the other files
            except error.ParserException as e:
                log.error(str(e))
                pass
            # this is critical
            except Exception as e:
                log.exception(e)
                raise

    end = timeit.default_timer() - start
    log.info("Finished AST Extraction in {:.5f}s".format(end))


if __name__ == '__main__':
    # we basically use vcsSHARK argparse config
    parser = argparse.ArgumentParser(description='Analyze the given URI. An URI should be a checked out GIT Repository.')
    parser.add_argument('-U', '--db-user', help='Database user name', default=None)
    parser.add_argument('-P', '--db-password', help='Database user password', default=None)
    parser.add_argument('-DB', '--db-database', help='Database name', default='vcsshark')
    parser.add_argument('-H', '--db-hostname', help='Name of the host, where the database server is running', default='localhost')
    parser.add_argument('-p', '--db-port', help='Port, where the database server is listening', default=27017, type=int)
    parser.add_argument('-i', '--input', help='Path to the checked out repository directory', required=True)
    parser.add_argument('-r', '--rev', help='Hash of the revision.', required=True)
    parser.add_argument('-u', '--url', help='URL of the project (e.g., GIT Url).', required=True)
    parser.add_argument('-a', '--db-authentication', help='Name of the authentication database')

    main(parser.parse_args())
