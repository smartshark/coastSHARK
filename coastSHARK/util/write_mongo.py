#!/usr/bin/env python

from mongoengine import *
from pycoshark.mongomodels import VCSSystem, File, Commit, CodeEntityState


class MongoDb(object):
    """This class just wraps the Mongo connection code and the query for fetching the correct CodeEntityState for inserting the AST information.
    """

    def __init__(self, host, port, db, user, password, authentication_source, vcs_url, revision):
        self.db = {'host': host, 'port': port, 'db': db, 'username': user, 'password': password, 'authentication_source': authentication_source}
        self.vcs_url = vcs_url
        self.revision = revision

    def connect(self):
        connect(**self.db)

    def write_imports(self, filepath, imports):
        """Write imports to code_entity_states.

        :param str filepath: The full path of this file.
        :param list imports: A list of strings containing the imports.
        """
        vcs = VCSSystem.objects.get(url=self.vcs_url)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        CodeEntityState.objects(commit_id=c.id, file_id=f.id, long_name=filepath).upsert_one(imports=imports)

    def write_node_type_counts(self, filepath, node_count, node_type_counts):
        """Write AST bag-of-words and number of AST nodes for this file to code_entity_states.

        :param str filepath: The full path of this file.
        :param int node_count: The number of AST nodes.
        :param dict node_type_counts: The number for each type of AST node.
        """
        vcs = VCSSystem.objects.get(url=self.vcs_url)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        tmp = {'set__metrics__{}'.format(k): v for k, v in node_type_counts.items()}
        tmp['set__metrics__node_count'] = node_count

        CodeEntityState.objects(commit_id=c.id, file_id=f.id, long_name=filepath).upsert_one(**tmp)
