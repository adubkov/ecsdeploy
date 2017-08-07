import mock

from unittest import TestCase
from unittest.runner import TextTestResult

from ..service import Service

# Suppress standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class MockECS(object):
    def __init__(self, res):
        self.res = res
    def describe_services(self, **kwargs):
        return self.res
    def create_service(self, **kwargs):
        return self.res
    def update_service(self, **kwargs):
        return self.res

class TestService(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service_name = 'test-service1'
        cls.task_definition = {
            'status': 'INACTIVE',
            'networkMode': 'bridge',
            'family': cls.service_name,
            'volumes': [
                {'host': {'sourcePath': '/etc/config.cfg'}, 'name': 'config'},
                {'host': {'sourcePath': '/data'}, 'name': 'db'}
            ],
            'taskDefinitionArn': 'mock:5',
            'containerDefinitions': [
                {
                    'memoryReservation': 3600,
                    'name': 'mock',
                    'mountPoints': [
                        {'sourceVolume': 'db', 'containerPath': '/data'},
                        {'sourceVolume': 'config', 'containerPath': '/etc/config.cfg'}
                    ],
                    'image': '12345678.dkr.ecr.us-west-2.amazonaws.com/release/mock:latest',
                    'cpu': 2,
                    'portMappings': [
                        {'protocol': 'tcp', 'containerPort': 8888, 'hostPort': 80}
                    ],
                    'essential': True,
                }
            ],
            'revision': 5
        }

        cls.cfg = {
            'service': {
                'name'   : 'test-service',
                'cluster': 'dev-ecs',
                'deployment': {
                    'maximum_percent': 100,
                    'minimum_healthy_percent': 0,
                },
                'desired_count': 1,
                'load_balancers': {
                    'http': {
                        'target_group_arn': 'arn://1234567890',
                        'container_name': 'mock',
                        'container_port': '8888',
                    }
                }
            },
            'role': 'iamRole',
        }

    def test_get(self):
        """TestService.get"""
        expect = {'serviceName': 'test-service', 'status': 'ACTIVE'}
        mock_services = {'services': [expect]}
        ecs = MockECS(mock_services)
        service = Service(ecs, self.cfg, self.task_definition)
        res = service.get()
        self.assertDictEqual(res, expect)

    def test_create(self):
        """TestService.create"""
        expect = {'serviceName': 'test-service', 'status': 'ACTIVE'}
        mock_service = {'service': [expect]}
        ecs = MockECS(mock_service)
        service = Service(ecs, self.cfg, self.task_definition)
        res = service.create()
        self.assertDictEqual(res.pop(), expect)

    def test_update(self):
        """TestService.update"""
        expect = {'serviceName': 'test-service', 'status': 'ACTIVE'}
        mock_service = {'service': [expect]}
        ecs = MockECS(mock_service)
        service = Service(ecs, self.cfg, self.task_definition)
        res = service.update()
        self.assertDictEqual(res.pop(), expect)
