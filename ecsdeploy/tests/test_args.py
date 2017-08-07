import mock

from unittest import TestCase
from unittest.runner import TextTestResult

from ..args import Arguments

# Suppress standard description output
TextTestResult.getDescription = lambda _, test: test.shortDescription()

class TestArguments(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.args = [
            '-e', 'dev',
            '-r', 'us-west-2',
            '-s', 'test-service',
            '-t', 'latest',
            '--revision', '1',
            '--cfg', 'service.desired_count=1',
            '--cfg', 'service.name=testname',
            '--var', 'LB_ARN=arn://something',
            '--var', 'test=True',
        ]

    def test_parse_argument_e(self):
        """TestArguments.envrironment"""
        res = Arguments(self.args)
        self.assertEqual(res['environment'], 'dev')

    def test_parse_argument_r(self):
        """TestArguments.region"""
        res = Arguments(self.args)
        self.assertEqual(res['region'], 'us-west-2')

    def test_parse_argument_s(self):
        """TestArguments.service"""
        res = Arguments(self.args)
        self.assertEqual(res['service'], 'test-service')

    def test_parse_argument_t(self):
        """TestArguments.tag"""
        res = Arguments(self.args)
        self.assertEqual(res['tag'], 'latest')

    def test_parse_argument_revision(self):
        """TestArguments.revision"""
        res = Arguments(self.args)
        self.assertEqual(res['revision'], '1')

    def test_parse_argument_cfg(self):
        """TestArguments.cfg"""
        res = Arguments(self.args)
        self.assertEqual(res['cfg'], ['service.desired_count=1', 'service.name=testname'])

    def test_parse_argument_var(self):
        """TestArguments.var"""
        res = Arguments(self.args)
        self.assertEqual(res['var'], ['LB_ARN=arn://something', 'test=True'])

    def test_parse_no_tag(self):
        """TestArguments.no_tag"""
        args = ['-e', 'dev', '-r', 'us-west-2', '-s', 'test-service']
        res = Arguments(self.args)
        self.assertEqual(res['tag'], 'latest')

    @mock.patch('argparse.ArgumentParser.error')
    def test_parse_no_argumens(self, mock_argparser_error):
        """TestArguments.no_arguments"""
        args = []
        mock_argparser_error.return_value = ''
        Arguments(args)
        mock_argparser_error.assert_called()

    @mock.patch('argparse.ArgumentParser.error')
    def test_parse_no_environment(self, mock_argparser_error):
        """TestArguments.no_environment"""
        args = ['-r', 'us-west-2', '-s', 'test-service']
        mock_argparser_error.return_value = ''
        Arguments(args)
        mock_argparser_error.assert_called()

    @mock.patch('argparse.ArgumentParser.error')
    def test_parse_no_region(self, mock_argparser_error):
        """TestArguments.no_region"""
        args = ['-e', 'dev', '-s', 'test-service']
        mock_argparser_error.return_value = ''
        Arguments(args)
        mock_argparser_error.assert_called()

    @mock.patch('argparse.ArgumentParser.error')
    def test_parse_no_service(self, mock_argparser_error):
        """TestArguments.no_service"""
        args = ['-e', 'dev', '-r', 'us-west-2']
        mock_argparser_error.return_value = ''
        Arguments(args)
        mock_argparser_error.assert_called()
