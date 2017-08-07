import mock
import os

from unittest import TestCase
from unittest.runner import TextTestResult

from ..ecsdeploy import ECSDeploy, main
from ..exceptions import ECSDeployException
from ..__init__ import __version__

# Suppres standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class MockECSDeploy(object):
    def __init__(self, code=None):
        self.code = code

    def start(self):
        if self.code:
            raise ECSDeployException(self.code, "error")
        else:
            return

class Checker(object):
    def __init__(self, n):
        self._checker = {'_max_attempts': n}

class Events(object):
    def __init__(self, n):
        self._unique_id_handlers = {
            'retry-config-ecs': {
                'handler': Checker(n)
            }
        }

class MockSession(object):
    def __init__(self, **kwargs):
        self.meta = Events(kwargs['n'])
        pass
    def client(self, **kwrgs):
        return self

class MockLogger(object):
    def __init__(self):
        pass
    def debug(self, *args):
        pass
    def info(self, *args):
        pass

class MockCluster(object):
    def __init__(self, res):
        self.res = res
    def get(self, **kwargs):
        return self.res
    def create(self, **kwargs):
        return self.res

class MockTaskDefinition(object):
    def __init__(self, res):
        self.res = res
    def get(self, *args):
        return self.res
    def register(self, **kwargs):
        return self.res

class MockService(object):
    def __init__(self, res=None):
        self.res = res
    def get(self, **kwargs):
        return self.res
    def create(self, **kwargs):
        return True
    def update(self, **kwargs):
        return self.res

class TestECSDeploy(TestCase):

    @mock.patch("os.environ.get")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._get_aws_client")
    @mock.patch("ecsdeploy.ecsdeploy.Logger")
    @mock.patch("boto3.session.Session")
    def setUp(self,
              mock_session,
              mock_logger,
              mock_ecsdeploy_get_aws_client,
              mock_os_environ_get):

        mock_os_environ_get.return_value = os.path.join(
            os.path.dirname(__file__), 'configs'
        )
        mock_session.return_value = MockSession(n=50)
        mock_logger.return_value = MockLogger()
        mock_ecsdeploy_get_aws_client.return_value = 'aws_ecs'


        args = [
           '-e', 'dev',
           '-r', 'us-west-2',
           '-s', 'test-service2',
           '--cfg', 'service.desired_count=10',
           '-c', 'service.name=test',
           '-v', 'test=True',
           '--var', 'tty=True',
           '-c', 'task.containers.mock.cpu=99',
           '--verify',
        ]
        self.ecsdeploy = ECSDeploy(args=args)

    def test_version_specified(self):
        """TestECSDeploy.test_version"""
        self.assertIsNotNone(__version__)

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy")
    def test_main_ok(self, mock_ecsdeploy):
        """TestECSDeploy.main(ok)"""
        mock_ecsdeploy.return_value = MockECSDeploy()
        self.assertIsNone(main())

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy")
    def test_main_failed(self, mock_ecsdeploy):
        """TestECSDeploy.main(failed)"""
        error = ECSDeployException("error")
        mock_ecsdeploy.return_value = MockECSDeploy(error)
        self.assertRaises(ECSDeployException, main)

    def test__get_aws_client(self):
        """TestECSDeploy._get_aws_client"""
        service = 'ecs'
        settings = dict(
            region = 'us-west-1',
        )
        res = self.ecsdeploy._get_aws_client(service, settings)
        self.assertEqual(res.meta.events._unique_id_handlers['retry-config-ecs']['handler']._checker.__dict__['_max_attempts'], 50)
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.Cluster")
    def test__create_cluster(self, mock_cluster):
        """TestECSDeploy._create_cluster"""
        mock_cluster.return_value = MockCluster("mock_cluster")
        res = self.ecsdeploy._create_cluster()
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.TaskDefinition")
    def test__register_task_definition(self, mock_task_definition):
        """TestECSDeploy._register_task_definition"""
        mock_task_definition.return_value = MockTaskDefinition("mock_task_definition")
        self.ecsdeploy.args['revision'] = None
        res = self.ecsdeploy._register_task_definition()
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.TaskDefinition")
    def test__register_task_definition_revision(self, mock_task_definition):
        """TestECSDeploy._register_task_definition(revision)"""
        mock_task_definition.return_value = MockTaskDefinition("mock_task_definition")
        self.ecsdeploy.args['revision'] = '1'
        res = self.ecsdeploy._register_task_definition()
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.Service")
    def test__create_or_update_service(self, mock_service):
        """TestECSDeploy._create_or_update_service"""
        mock_service.return_value = MockService({'taskDefinition':'task-definition/mock:1'})
        task_definition = dict(
            taskDefinitionArn="task-definition/mock:1",
        )
        res = self.ecsdeploy._create_or_update_service(task_definition)
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.Service")
    def test__create_or_update_service_create(self, mock_service):
        """TestECSDeploy._create_or_update_service(create)"""
        mock_service.return_value = MockService()
        res = self.ecsdeploy._create_or_update_service()
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.Service")
    def test__create_or_update_service_update(self, mock_service):
        """TestECSDeploy._create_or_update_service(update)"""
        mock_service.return_value = MockService({'taskDefinition':'task-definition/mock:2'})
        task_definition = dict(
            taskDefinitionArn="task-definition/mock:1",
        )
        res = self.ecsdeploy._create_or_update_service(task_definition)
        self.assertTrue(res)

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_cluster")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._register_task_definition")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_or_update_service")
    def test_start(self,
                   mock_create_or_update_service,
                   mock_register_task_definition,
                   mock_create_cluster):
        """TestECSDeploy.start"""
        service = dict(
            taskDefinition = 'arn',
            serviceName = 'mock-service',
        )
        task_definition = dict(
            taskDefinitionArn = 'arn',
            family = 'mock-family',
            revision = '1',
        )
        mock_create_or_update_service.return_value = service
        mock_register_task_definition.return_value = task_definition
        mock_create_cluster.return_value = True
        self.ecsdeploy.args['verify'] = False
        self.ecsdeploy.start()

    def test_start_print(self):
        """TestECSDeploy.start(print)"""
        self.ecsdeploy.args['print'] = True
        res = self.ecsdeploy.start()

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_cluster")
    def test_start_no_cluster(self, mock_create_cluster):
        """TestECSDeploy.start(no cluster)"""
        mock_create_cluster.return_value = None
        self.assertRaises(ECSDeployException, self.ecsdeploy.start)

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_cluster")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._register_task_definition")
    def test_start_no_task_definition(self,
                   mock_register_task_definition,
                   mock_create_cluster):
        """TestECSDeploy.start(no task definition)"""
        mock_register_task_definition.return_value = None
        mock_create_cluster.return_value = True
        self.assertRaises(ECSDeployException, self.ecsdeploy.start)

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_cluster")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._register_task_definition")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_or_update_service")
    def test_start_no_service(self,
                   mock_create_or_update_service,
                   mock_register_task_definition,
                   mock_create_cluster):
        """TestECSDeploy.start(no service)"""
        mock_create_or_update_service.return_value = None
        mock_register_task_definition.return_value = True
        mock_create_cluster.return_value = True
        self.assertRaises(ECSDeployException, self.ecsdeploy.start)

    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_cluster")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._register_task_definition")
    @mock.patch("ecsdeploy.ecsdeploy.ECSDeploy._create_or_update_service")
    def test_start_verify(self,
                   mock_create_or_update_service,
                   mock_register_task_definition,
                   mock_create_cluster):
        """TestECSDeploy.start(verify)"""
        mock_create_or_update_service.return_value = True
        mock_register_task_definition.return_value = True
        mock_create_cluster.return_value = True
        self.ecsdeploy.args['verify'] = True
        self.ecsdeploy.start()
