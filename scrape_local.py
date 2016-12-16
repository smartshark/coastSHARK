#!/usr/bin/env python

import os
import argparse
import tempfile
import subprocess

from mongoengine import connect
from git import Repo

from coastSHARK.smartshark_plugin import main as coast
from coastSHARK.util.mongomodels import Project  # we need to create the project first if it is new

# todo:
# - clean up self_args and redundancies
# - centralize configuration parameters

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
        self._name = args.name

        self._create_project(args.name)

    def _create_project(self, name):
        connect(host='localhost', port=27017, db='smartshark4', username='root', password='balla', authentication_source='smartshark4')
        Project.objects(name=name).upsert_one(name=name)

    def _checkout_revision(self, revision):
        self._repo.git.checkout(revision)

    def _run_programs_repo(self):
        args = {'db_hostname': 'localhost',
                'db_port': 27017,
                'db_database': 'smartshark4',
                'db_user': 'root',
                'db_password': 'balla',
                'db_authentication': 'smartshark4',
                'url': self._args.url,
                'input': self._path,
                'name': self._name,
                }

        pbin = '/srv/www/vcsSHARK/bin/python'
        cmd = [pbin, '/srv/www/vcsSHARK/vcsshark.py', '-D', 'mongo', '-U', args['db_user'], '-P', args['db_password'], '-DB', args['db_database'], '-H', args['db_hostname'], '-a', args['db_authentication'], '--path', self._path, '-n', self._name]

        out = subprocess.check_output(cmd)
        print(out)

    def _run_programs_rev(self, revision):
        args = {'db_hostname': 'localhost',
                'db_port': 27017,
                'db_database': 'smartshark4',
                'db_user': 'root',
                'db_password': 'balla',
                'db_authentication': 'smartshark4',
                'url': self._args.url,
                'rev': revision.hexsha,
                'input': self._path
                }

        # pass argparse namespace object like expected
        tmp = argparse.Namespace()
        for k, v in args.items():
            setattr(tmp, k, v)


        print('running mecoSHARK for: {}'.format(tmp.rev))
        pbin = '/srv/www/mecoSHARK/bin/python'
        cmd = [pbin,
               '/srv/www/mecoSHARK/main.py',
               '-U', args['db_user'],
               '-P', args['db_password'],
               '-DB', args['db_database'],
               '-H', args['db_hostname'],
               '-a', args['db_authentication'],
               '-i', args['input'],
               '-o', args['input'],
               '-r', args['rev'],
               '-u', args['url']]
        out = subprocess.check_output(cmd)
        print(out)

        # now the real deal
        print('running coastSHARK for: {}'.format(tmp.rev))
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
    parser.add_argument('-n', '--name', help='Project Name')
    g = GitScrape(parser.parse_args())
    g.run()
