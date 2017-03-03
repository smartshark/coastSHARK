#!/usr/bin/env python

from mongoengine import *
from pycoshark.mongomodels import VCSSystem, File, Commit, CodeEntityState
from pycoshark.utils import get_code_entity_state_identifier, create_mongodb_uri_string



class MongoDb(object):
    """This class just wraps the Mongo connection code and the query for fetching the correct CodeEntityState for inserting the AST information.
    """

    def __init__(self, database, user, password, host, port, authentication, ssl, vcs_url, revision):
        self.vcs_url = vcs_url
        self.revision = revision
        self.database = database
        self.uri = create_mongodb_uri_string(user, password, host, port, authentication, ssl)
        

    def connect(self):
        connect(self.database, host=self.uri)

    def write_imports(self, filepath, imports):
        """Write imports to code_entity_states.

        :param str filepath: The full path of this file.
        :param list imports: A list of strings containing the imports.
        """
        vcs = VCSSystem.objects.get(url=self.vcs_url)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        s_key = get_code_entity_state_identifier(filepath, c.id, f.id)

        CodeEntityState.objects(s_key=s_key).upsert_one(imports=imports)

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

        s_key = get_code_entity_state_identifier(filepath, c.id, f.id)

        CodeEntityState.objects(s_key=s_key).upsert_one(**tmp)
