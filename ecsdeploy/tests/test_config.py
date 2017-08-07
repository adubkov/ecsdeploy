import mock
import os

from unittest import TestCase
from unittest.runner import TextTestResult

from ..config import Config

# Suppress standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class TestConfig(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_config_dir = os.path.join(os.path.dirname(__file__), 'configs')

    def test_init(self):
        """TestConfig.__init__"""
        cfg = Config(self.mock_config_dir, 'dev', 'us-west-2', 'test-service3', 'latest', [], [])
        self.assertTrue(cfg)

    def test__generate_effective_container_config(self):
        """TestConfig._generate_effective_container_config"""
        res = dict(
            mock_container = dict(
                cpu = 1,
                memory = 1024,
            )
        )

        values = dict(
            memory = 512,
            options = dict(key='value'),
        )

        expect = dict(
            mock_container = dict(
                cpu = 1,
                memory = 512,
                options = dict(key='value'),
            )
        )

        Config._generate_effective_container_config(res, values, 'mock_container')

        self.assertDictEqual(res, expect)

    def test__generate_effective_container_config_non_dict(self):
        """TestConfig._generate_effective_container_config(non dict)"""
        res = [1, 2, 3]

        values = dict(
            memory = 512,
        )

        expect = [1, 2, 3]

        Config._generate_effective_container_config(res, values, 'mock_container')

        self.assertListEqual(res, expect)


    def test__merge_list(self):
        """TestConfig._merge(list)"""
        o1 = [1, 2]
        o2 = [3]
        expect = [1, 2, 3]
        res = Config._merge(o1, o2)
        self.assertListEqual(res, expect)

    def test__merge_dict(self):
        """TestConfig._merge(dict)"""
        o1 = dict(
            test=dict(key1=1)
        )
        o2 = dict(
            test=dict(key2=2)
        )
        expect = dict(
            test=dict(
                key1=1,
                key2=2,
            )
        )
        res = Config._merge(o1, o2)
        self.assertDictEqual(res, expect)
