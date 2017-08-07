import mock
import os

from unittest import TestCase
from unittest.runner import TextTestResult

from ..task_definition import *
from ..config import Config

# Suppress standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class MockECS(object):
    def __init__(self, res={}):
        self.res = res
    def describe_task_definition(self, **kwargs):
        return self.res
    def register_task_definition(self, **kwargs):
        return self.res

class TestTaskDefinition(TestCase):

    @classmethod
    def setUpClass(cls):
        region = 'us-west-2'
        cluster_name = 'dev-ecs'
        cls.ecs = MockECS()
        cls.response_metadata = {
            'RetryAttempts': 0,
            'HTTPStatusCode': 200,
            'RequestId': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
            'HTTPHeaders': {
                'x-amzn-requestid': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'content-length': '937',
                'server': 'Server',
                'connection': 'keep-alive',
                'date': 'Mon, 31 Jul 2017 22:43:41 GMT',
                'content-type': 'application/x-amz-json-1.1'
            }
        }
        cls.expect = {
            'status': 'ACTIVE',
            'networkMode': 'bridge',
            'family': 'mock',
            'placementConstraints': [],
            'requiresAttributes': [
                {'name': 'com.amazonaws.ecs.capability.ecr-auth'},
                {'name': 'com.amazonaws.ecs.capability.docker-remote-api.1.21'}
            ],
            'volumes': [
                {'host': {'sourcePath': '/etc/config.cfg'}, 'name': 'config'},
                {'host': {'sourcePath': '/data'}, 'name': 'db'}
            ],
            'taskDefinitionArn': 'arn:aws:ecs:us-west-2:12345678:task-definition/mock:5',
            'containerDefinitions': [{
                'memoryReservation': 1024,
                'environment': [],
                'name': 'mock',
                'mountPoints': [{
                    'sourceVolume': 'db',
                    'containerPath': '/data'
                }, {
                    'sourceVolume': 'config',
                    'containerPath': '/etc/config.cfg'
                }
                ],
                'image': '12345678.dkr.ecr.us-west-2.amazonaws.com/release/mock:latest',
                'cpu': 10,
                'portMappings': [
                    {
                        'protocol': 'tcp',
                        'containerPort': 8080,
                        'hostPort': 80
                    }
                ],
                'essential': True,
                'volumesFrom': []
            }],
            'revision': 5
        }

        cls.mock_config_dir = os.path.join(os.path.dirname(__file__), 'configs')

    def test_make_volumes(self):
        """TestTaskDefinition.make_volumes"""
        m = {'logs': '/var/log'}
        expect = {'host': {'sourcePath': '/var/log'}, 'name': 'logs'}
        res = make_volumes(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_port_mapping(self):
        """TestTaskDefinition.make_port_mapping"""
        m = [{'host_port': 80, 'protocol': 'tcp', 'container_port': 8080}]
        expect = {'protocol': 'tcp', 'containerPort': 8080, 'hostPort': 80}
        res = make_port_mapping(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_environment(self):
        """TestTaskDefinition.make_environment"""
        m = {'tty': 'true'}
        expect = {'name': 'tty', 'value': 'true'}
        res = make_environment(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_mount_points(self):
        """TestTaskDefinition.make_mount_points"""
        m = {'/var/log': {
                'source_volume': 'logs',
                'read_only': True,
            }
        }
        expect = {'containerPath': '/var/log', 'sourceVolume': 'logs', 'readOnly': True}
        res = make_mount_points(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_volumes_from(self):
        """TestTaskDefinition.make_volumes_from"""
        m = {'monitor': {'read_only': True}}
        expect = {'sourceContainer': 'monitor', 'readOnly': True}
        res = make_volumes_from(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_extra_hosts(self):
        """TestTaskDefinition.make_extra_hosts"""
        m = {'dns.local': '10.0.0.1'}
        expect = {'hostname': 'dns.local', 'ipAddress': '10.0.0.1'}
        res = make_extra_hosts(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_ulimits(self):
        """TestTaskDefinition.make_ulimits"""
        m = {'collectd': {'soft': 100, 'hard': 100}}
        expect = {'name': 'collectd', 'softLimit': 100, 'hardLimit': 100}
        res = make_ulimits(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_make_log_configuration(self):
        """TestTaskDefinition.make_log_configuration"""
        m = {'log_driver': 'awslogs', 'options': {'KeyName1': 1, 'KeyName2': 2}}
        expect = {'logDriver': 'awslogs', 'options': {'KeyName1': 1, 'KeyName2': 2}}
        res = make_log_configuration(m)
        self.assertIsInstance(res, dict, "Return type should be dict.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res, expect)

    def test_make_container(self):
        """TestTaskDefinition.make_container"""
        m = {
            'mock': {
                'mount_points': {
                    '/data': {'source_volume': 'db'},
                    '/etc/config.cfg': {'source_volume': 'config'}
                },
                'image': '12345678.dkr.ecr.us-west-2.amazonaws.com/release/mock:latest',
                'namespace': 'release',
                'essential': True,
                'memory_reservation': 1024,
                'environment_variables': {},
                'port_mappings': [
                    {'host_port': 80, 'protocol': 'tcp', 'container_port': 8080}
                ],
                'cpu': 10
            }
        }
        expect = {
            'memoryReservation': 1024,
            'mountPoints': [
                {'sourceVolume': 'db', 'containerPath': '/data'},
                {'sourceVolume': 'config', 'containerPath': '/etc/config.cfg'},
            ],
            'name': 'mock',
            'image': '12345678.dkr.ecr.us-west-2.amazonaws.com/release/mock:latest',
            'cpu': 10,
            'portMappings': [
                {'protocol': 'tcp', 'containerPort': 8080, 'hostPort': 80}
            ],
            'essential': True
        }
        res = make_container(m)
        self.assertIsInstance(res, list, "Return type should be list.")
        self.assertTrue(len(res), "Return no results. Possible empty dict passed in test.")
        self.assertDictEqual(res[0], expect)

    def test_get(self):
        """TestTaskDefinition.get"""
        self.ecs.res = {
            'ResponseMetadata': self.response_metadata,
            'taskDefinition': self.expect
        }
        revision = '5'

        cfg = Config(self.mock_config_dir, 'dev', 'us-west-2', 'test-service1', 'latest', [], [])
        task_definition = TaskDefinition(self.ecs, cfg)
        res = task_definition.get(revision)
        self.assertDictEqual(res, self.expect)

    def test_register_service1(self):
        """TestTaskDefinition.register(test-service1)"""
        self.ecs.res = {
            'ResponseMetadata': self.response_metadata,
            'taskDefinition': self.expect
        }

        cfg = Config(
            self.mock_config_dir,
            'dev',
            'us-west-2',
            'test-service1',
            'latest'
        )

        task_definition = TaskDefinition(self.ecs, cfg)
        res = task_definition.register()
        self.assertDictEqual(res, self.expect)

    def test_register_service2(self):
        """TestTaskDefinition.register(test-service2)"""
        self.ecs.res = {
            'ResponseMetadata': self.response_metadata,
            'taskDefinition': self.expect
        }

        cfg = Config(
            self.mock_config_dir,
            'prd',
            'us-west-2',
            'test-service2',
            'latest',
            ["token=ABCDEF-1234-1234-1234-XYZ"],
            ["service.desired_count=2", "task.containers.mock.memory=2048"]
        )

        task_definition = TaskDefinition(self.ecs, cfg)
        res = task_definition.register()
        self.assertDictEqual(res, self.expect)
