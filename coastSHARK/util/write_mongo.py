#!/usr/bin/env python

import logging

from mongoengine import connect
from pycoshark.mongomodels import Project, VCSSystem, File, Commit, CodeEntityState
from pycoshark.utils import get_code_entity_state_identifier, create_mongodb_uri_string
from .complexity_java import SourcemeterConversion


class MongoDb(object):
    """This class just wraps the Mongo connection code and the query for fetching the correct CodeEntityState for inserting the AST information."""

    def __init__(self, database, user, password, host, port, authentication, ssl, project_name, vcs_url, revision):
        self.project_name = project_name
        self.vcs_url = vcs_url
        self.revision = revision
        self.database = database
        self.uri = create_mongodb_uri_string(user, password, host, port, authentication, ssl)
        self._log = logging.getLogger('coastSHARK')

    def connect(self):
        connect(self.database, host=self.uri)

    def write_imports(self, filepath, imports):
        """Write imports to code_entity_states.

        :param str filepath: The full path of this file.
        :param list imports: A list of strings containing the imports.
        """
        project = Project.objects.get(name=self.project_name)
        vcs = VCSSystem.objects.get(url=self.vcs_url, project_id=project.id)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        s_key = get_code_entity_state_identifier(filepath, c.id, f.id)

        CodeEntityState.objects(s_key=s_key).upsert_one(imports=imports, ce_type='file', long_name=filepath, commit_id=c.id, file_id=f.id)

    def write_node_type_counts(self, filepath, node_count, node_type_counts):
        """Write AST bag-of-words and number of AST nodes for this file to code_entity_states.

        :param str filepath: The full path of this file.
        :param int node_count: The number of AST nodes.
        :param dict node_type_counts: The number for each type of AST node.
        """
        project = Project.objects.get(name=self.project_name)
        vcs = VCSSystem.objects.get(url=self.vcs_url, project_id=project.id)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        tmp = {'set__metrics__{}'.format(k): v for k, v in node_type_counts.items()}
        tmp['set__metrics__node_count'] = node_count
        tmp['ce_type'] = 'file'
        tmp['long_name'] = filepath
        tmp['commit_id'] = c.id
        tmp['file_id'] = f.id

        s_key = get_code_entity_state_identifier(filepath, c.id, f.id)

        CodeEntityState.objects(s_key=s_key).upsert_one(**tmp)

    def write_method_metrics(self, filepath, method_data):
        """Write additional method metrics.

        :param str filepath: The full path of this file.
        :param dict method_data: The extracted method metrics.
        """
        project = Project.objects.get(name=self.project_name)
        vcs = VCSSystem.objects.get(url=self.vcs_url, project_id=project.id)
        c = Commit.objects.get(revision_hash=self.revision, vcs_system_id=vcs.id)
        f = File.objects.get(path=filepath, vcs_system_id=vcs.id)

        sc = SourcemeterConversion()

        for m in method_data:
            path = '{}.{}.{}('.format(m['package_name'], m['class_name'], m['method_name'])
            match_long_name = sc.get_sm_long_name(m)

            if CodeEntityState.objects.filter(long_name__startswith=path, commit_id=c.id, file_id=f.id, ce_type='method').count() == 0:
                self._log.error('[METHOD NOT FOUND] long_name: {}, commit_id: {}, file_id: {}, probably wrong method path'.format(path, c.id, f.id))
                continue

            # we have only one match, this is simple as we just write the data
            if CodeEntityState.objects.filter(long_name__startswith=path, commit_id=c.id, file_id=f.id, ce_type='method').count() == 1:
                ces = CodeEntityState.objects.filter(long_name__startswith=path, commit_id=c.id, file_id=f.id, ce_type='method')[0]
                long_name = ces.long_name

                s_key = get_code_entity_state_identifier(long_name, c.id, f.id)
                tmp = {}
                tmp['set__metrics__cognitive_complexity_sonar'] = m['cognitive_complexity_sonar']
                tmp['set__metrics__cyclomatic_complexity_test'] = m['cyclomatic_complexity']

                CodeEntityState.objects(s_key=s_key).upsert_one(**tmp)
                continue

            # we have more than one we need to match method signatures
            for ces in CodeEntityState.objects.filter(long_name__startswith=path, commit_id=c.id, file_id=f.id, ce_type='method'):

                # we just remove dots, $ and / from params in this so that we have a chance to match against our match_long_name
                match_long_name2 = sc.get_sm_long_name2(ces.long_name)

                # new way:, first one is with long = J second with long = L
                # does not work with_ org.apache.zookeeper.server.quorum.Zab1_0Test$5.proposeNewSession(LQuorumPacket;LL)V
                # this gets merged to org.apache.zookeeper.server.quorum.Zab1_0Test$5.proposeNewSession(LQuorumPacket;LL;)V
                # therefore we include the original long name
                if match_long_name[0] == match_long_name2 or match_long_name[1] == match_long_name2 or ces.long_name in match_long_name:

                    long_name = ces.long_name

                    s_key = get_code_entity_state_identifier(long_name, c.id, f.id)
                    tmp = {}
                    tmp['set__metrics__cognitive_complexity_sonar'] = m['cognitive_complexity_sonar']
                    tmp['set__metrics__cyclomatic_complexity_test'] = m['cyclomatic_complexity']

                    CodeEntityState.objects(s_key=s_key).upsert_one(**tmp)
                    break
            else:
                self._log.error('[NO MATCH] have: path: {}, params: {}, return_type: {}, merged long_name: {}'.format(path, m['parameter_types'], m['return_type'], match_long_name))
                for c1 in CodeEntityState.objects.filter(long_name__startswith=path, commit_id=c.id, file_id=f.id, ce_type='method'):
                    param, ret = sc.get_sm_params(c1.long_name)
                    self._log.error('[NO MATCH] searched: long_name: {}, params: {}, return_type: {}, merged long_name: {}'.format(c1.long_name, param, ret, match_long_name2))
