from mongoengine import *
from util.mongomodels import Project, File, Import, NodeTypeCount, Commit

# todo: extract our models from mongomodels, just use mongomodels


class MongoDb(object):

    def __init__(self, host, port, db, user, password):
        self.db = {'host': host, 'port': port, 'db': db, 'username': user, 'password': password}

    def connect(self):
        connect(**self.db)

    def write_imports(self, project_url, revision, filepath, imports):
        pr = Project.objects.get(url=project_url)
        c = Commit.objects.get(revisionHash=revision, projectId=pr.id)
        f = File.objects.get(path=filepath)

        Import.objects(commitId=c.id, fileId=f.id).upsert_one(imports=imports)

    def write_node_type_counts(self, project_url, revision, filepath, node_count, node_type_counts):
        pr = Project.objects.get(url=project_url)
        c = Commit.objects.get(revisionHash=revision, projectId=pr.id)
        f = File.objects.get(path=filepath)

        NodeTypeCount.objects(commitId=c.id, fileId=f.id).upsert_one(nodeCount=node_count, nodeTypeCounts=node_type_counts)
