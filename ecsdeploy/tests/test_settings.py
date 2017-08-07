from mock import patch
from unittest import TestCase
from unittest.runner import TextTestResult

from ..settings import Settings

# Suppres standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class TestSettings(TestCase):

    @classmethod
    def setUp(cls):
        cls.args = {
            'service': 'test-service',
            'region': 'us-west-2',
            'revision': '5',
            'debug': True
        }

        cls.patcher = patch('os.environ.get')
        cls.environ_get_mock = cls.patcher.start()
        cls.environ_get_mock.return_value = '/home/user/configs'

    def test_settings_ecsdeploy_config(self):
        """TestSettings.ECSDEPLOY_CONFIG"""
        ecsdeploy_config = '/home/user/configs'
        res = Settings(self.args)
        self.assertEqual(res['ECSDEPLOY_CONFIG'], ecsdeploy_config)

    def test_settings_service(self):
        """TestSettings.service"""
        res = Settings(self.args)
        self.assertEqual(res['service'], 'test-service')

    def test_settings_region(self):
        """TestSettings.region"""
        res = Settings(self.args)
        self.assertEqual(res['region'], 'us-west-2')

    def test_settings_tag(self):
        """TestSettings.revision"""
        res = Settings(self.args)
        self.assertEqual(res['revision'], '5')

    def test_settings_debug(self):
        """TestSettings.debug"""
        res = Settings(self.args)
        self.assertTrue(res['debug'])
