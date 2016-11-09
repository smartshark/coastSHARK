from mongoengine import *
from util.mongomodels import Project, File, Import, NodeTypeCount, Commit

# todo: extract our models from mongomodels, just use mongomodels


class MongoDb(object):

    def __init__(self, host, port, db, user, password, authentication_source, project_url, revision):
        self.db = {'host': host, 'port': port, 'db': db, 'username': user, 'password': password, 'authentication_source': authentication_source}
        self.project_url = project_url
        self.revision = revision

    def connect(self):
        connect(**self.db)

    def write_imports(self, filepath, imports):
        pr = Project.objects.get(url=self.project_url)
        c = Commit.objects.get(revisionHash=self.revision, projectId=pr.id)
        f = File.objects.get(path=filepath, projectId=pr.id)

        Import.objects(commitId=c.id, fileId=f.id).upsert_one(imports=imports)

    def write_node_type_counts(self, filepath, node_count, node_type_counts):
        pr = Project.objects.get(url=self.project_url)
        c = Commit.objects.get(revisionHash=self.revision, projectId=pr.id)
        f = File.objects.get(path=filepath, projectId=pr.id)

        NodeTypeCount.objects(commitId=c.id, fileId=f.id).upsert_one(nodeCount=node_count, nodeTypeCounts=node_type_counts)
