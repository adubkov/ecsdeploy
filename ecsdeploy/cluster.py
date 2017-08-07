import logging

from .exceptions import ECSDeployException

class Cluster(object):
    def __init__(self, ecs, region, cluster_name):
        self.log = logging.getLogger(__name__)
        self.ecs = ecs
        self.region = region
        self.cluster_name = cluster_name

    def get(self):
        # Search cluster by name
        clusters = {}
        res = self.ecs.describe_clusters(clusters=[self.cluster_name])
        if not res:
            self.log.debug("Cluster '%s' is not exist.", self.cluster_name)
        else:
            # Filter only active clusters
            clusters = list(filter(lambda x: x['status'] == 'ACTIVE', res['clusters']))
            if not clusters:
                self.log.debug("Cluster '%s' exist but not 'ACTIVE'", self.cluster_name)
            if len(clusters) > 1:
                raise ECSDeployException(
                    "More than one cluster found for name '%s'. Please verify "
                    "cluster name. Result: %s" % (self.cluster_name, clusters))

        return clusters.pop() if clusters else {}

    def create(self):
        res = self.ecs.create_cluster(clusterName=self.cluster_name)

        if res['cluster']['status'] == 'INACTIVE':
            raise ECSDeployException(
                ("New cluster '%s' has been created but it is not 'ACTIVE' "
                "yet.") % self.cluster_name)

        self.log.debug("New cluster '%s' have been created in '%s' region.",
            self.cluster_name, self.region)

        return res['cluster']
