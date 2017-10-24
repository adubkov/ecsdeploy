import argparse
import logging
import json

try:
    from UserDict import UserDict
except ImportError: # pragma nocover
    from collections import UserDict

class Arguments(UserDict, object):
    def __init__(self, args=None):
        self.log = logging.getLogger(__name__)
        self.data = self._parse_arguments(args)
        self.log.debug("Parsed arguments: %s", self.data)

    def _parse_arguments(self, args=None):
        """Parse arguments.

        :type args: list
        :param args: Command line arguments. By default it will use sys.argv

        :rtype: dict
        :return: Parsed arguments.
        """
        parser = argparse.ArgumentParser()

        parser.add_argument('-e',
                            '--environment',
                            required=True,
                            help='Environment name')

        parser.add_argument('-r',
                            '--region',
                            required=True,
                            help='Region name')

        parser.add_argument('-s',
                            '--service',
                            required=True,
                            help='Service name')

        parser.add_argument('-t',
                            '--tag',
                            default='latest',
                            help='Container Tag')

        parser.add_argument('--revision',
                            help='Deploy existed revision of task definition.')

        parser.add_argument('-v',
                            '--var',
                            default=[],
                            action='append',
                            help='Pass variable into config. Example "debug=False" => {{ debug }} (pre-processing initial config).')

        parser.add_argument('-c',
                            '--cfg',
                            default=[],
                            action='append',
                            help='Example "service.desired_count=10" (post-processing result config).')

        parser.add_argument('--aws-profile',
                            help='~/.aws/credentials profile to use.')

        parser.add_argument('-p',
                            '--print',
                            default=False,
                            action='store_true',
                            help='Print effective config and exit.')

        parser.add_argument('--verify',
                            default=False,
                            action='store_true',
                            help='Wait for successful verification of the service update.')

        parser.add_argument('-D',
                            '--debug',
                            default=False,
                            action='store_true',
                            help='Change verbosity level to DEBUG')

        result = parser.parse_args(args)

        return vars(result)
