import os

from mongoengine import *
from .mongomodels import VCSSystem, File, Commit, CodeEntityState

# todo: extract our models from mongomodels, just use mongomodels


class MongoDb(object):

    def __init__(self, host, port, db, user, password, authentication_source, vcs_url, revision):
        self.db = {'host': host, 'port': port, 'db': db, 'username': user, 'password': password, 'authentication_source': authentication_source}
        self.vcs_url = vcs_url
        self.revision = revision

    def connect(self):
        connect(**self.db)

    def write_imports(self, filepath, imports):
        vcs = VCSSystem.objects.get(url=self.vcs_url)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        CodeEntityState.objects(commit_id=c.id, file_id=f.id, long_name=filepath).upsert_one(imports=imports)

    def write_node_type_counts(self, filepath, node_count, node_type_counts):
        tmp = {'node_count': node_count, 'node_type_counts': node_type_counts}

        vcs = VCSSystem.objects.get(url=self.vcs_url)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        CodeEntityState.objects(commit_id=c.id, file_id=f.id, long_name=filepath).upsert_one(metrics=tmp)
