#!/usr/bin/env python

import os
import argparse
import tempfile
import subprocess

from coastSHARK.smartshark_plugin import main as coast

from git import Repo


class GitScrape(object):

    def __init__(self, args):
        if args.path:
            self._path = args.path
        else:
            self._path = tempfile.mkdtemp()

        # clone and access
        if not os.path.isdir(self._path):
            Repo.clone_from(args.url, self._path)
        self._repo = Repo(self._path)
        self._args = args

    def _checkout_revision(self, revision):
        self._repo.git.checkout(revision)

    def _run_programs_repo(self):
        args = {'db_hostname': 'localhost',
                'db_port': 27017,
                'db_database': 'smartshark',
                'db_user': 'root',
                'db_password': 'balla',
                'db_authentication': 'smartshark',
                'url': self._args.url,
                'input': self._path
                }

        pbin = '/srv/www/vcsSHARK/bin/python'
        cmd = [pbin, '/srv/www/vcsSHARK/vcsshark.py', '-D', 'mongo', '-U', args['db_user'], '-P', args['db_password'], '-DB', args['db_database'], '-H', args['db_hostname'], '-a', args['db_authentication'], '-u', self._path]

        out = subprocess.check_output(cmd)
        print(out)

    def _run_programs_rev(self, revision):
        args = {'db_hostname': 'localhost',
                'db_port': 27017,
                'db_database': 'smartshark',
                'db_user': 'root',
                'db_password': 'balla',
                'db_authentication': 'smartshark',
                'url': self._args.url,
                'rev': revision.hexsha,
                'input': self._path
                }

        # pass argparse namespace object like expected
        tmp = argparse.Namespace()
        for k, v in args.items():
            setattr(tmp, k, v)

        print('running for: {}'.format(tmp.rev))
        coast(tmp)

    def run(self):
        self._run_programs_repo()
        for rev in list(self._repo.iter_commits(self._args.branch, max_count=self._args.max_count)):
            self._checkout_revision(rev)
            self._run_programs_rev(rev)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check out every revision.')
    parser.add_argument('-b', '--branch', help='Git branch to use', default='master')
    parser.add_argument('-m', '--max_count', help='Max number of Revisions', default=None)
    parser.add_argument('-u', '--url', help='URL of the Repo', required=True)
    parser.add_argument('-p', '--path', help='Persistent path of working dir for Repos.')
    g = GitScrape(parser.parse_args())
    g.run()
