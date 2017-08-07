import mock

from unittest import TestCase
from unittest.runner import TextTestResult

from ..cluster import Cluster
from ..exceptions import ECSDeployException

# Suppress standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class MockECS(object):
    def __init__(self, res):
        self.res = res
    def describe_clusters(self, **kwargs):
        return self.res
    def create_cluster(self, **kwargs):
        return self.res

class TestCluster(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster_name = 'ecs-dev'
        cls.region = 'us-west-2'

    def test_get(self):
        """TestCluster.get"""
        clusters = {
            # Response for describe_clusters
            'clusters': [
                {
                    'status': 'ACTIVE',
                    'clusterName': self.cluster_name,
                    'registeredContainerInstancesCount': 1,
                    'pendingTasksCount': 0,
                    'runningTasksCount': 1,
                    'activeServicesCount': 1,
                    'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
                }
            ],
            'failures': []
        }
        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        res = cluster.get()
        self.assertEqual(res['clusterName'], self.cluster_name)

    def test_get_inactive(self):
        """TestCluster.get(inactive)"""
        clusters = {
            # Response for describe_clusters
            'clusters': [
                {
                    'status': 'INACTIVE',
                    'clusterName': self.cluster_name,
                    'registeredContainerInstancesCount': 1,
                    'pendingTasksCount': 0,
                    'runningTasksCount': 1,
                    'activeServicesCount': 1,
                    'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
                }
            ],
            'failures': []
        }
        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        res = cluster.get()
        self.assertTrue(not res)

    def test_get_multiple_clusters_found(self):
        """TestCluster.get(multiple clusters found)"""
        clusters = {
            # Response for describe_clusters
            'clusters': [
                {
                    'status': 'ACTIVE',
                    'clusterName': self.cluster_name,
                    'registeredContainerInstancesCount': 1,
                    'pendingTasksCount': 0,
                    'runningTasksCount': 1,
                    'activeServicesCount': 1,
                    'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
                },
                {
                    'status': 'ACTIVE',
                    'clusterName': self.cluster_name,
                    'registeredContainerInstancesCount': 1,
                    'pendingTasksCount': 0,
                    'runningTasksCount': 1,
                    'activeServicesCount': 1,
                    'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
                }
            ],
            'failures': []
        }
        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        self.assertRaises(ECSDeployException, cluster.get)

    def test_get_not_exist(self):
        """TestCluster.get(not exist)"""
        clusters = {}
        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        res = cluster.get()
        self.assertTrue(not res)

    def test_create(self):
        """TestCluster.create"""
        clusters = {
            # Response for create_cluster
            'cluster': {
                'status': 'ACTIVE',
                'clusterName': self.cluster_name,
                'registeredContainerInstancesCount': 1,
                'pendingTasksCount': 0,
                'runningTasksCount': 1,
                'activeServicesCount': 1,
                'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
            },
            'failures': []
        }

        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        res = cluster.create()
        self.assertEqual(res['clusterName'], self.cluster_name)

    def test_create_exist(self):
        """TestCluster.create(inactive)"""
        clusters = {
            # Response for create_cluster
            'cluster': {
                'status': 'INACTIVE',
                'clusterName': self.cluster_name,
                'registeredContainerInstancesCount': 1,
                'pendingTasksCount': 0,
                'runningTasksCount': 1,
                'activeServicesCount': 1,
                'clusterArn': 'arn:aws:ecs:us-west-2:mock:cluster/ecs-dev',
            },
            'failures': []
        }

        ecs = MockECS(clusters)
        cluster = Cluster(ecs, self.region, self.cluster_name)
        self.assertRaises(ECSDeployException, cluster.create)
