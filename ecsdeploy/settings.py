import logging
import os
import sys

try:
    from UserDict import UserDict
except ImportError: # pragma nocover
    from collections import UserDict

class Settings(UserDict, object):

    data = {}

    def __init__(self, args):
        self.log = logging.getLogger(__name__)
        self._read_envars()
        self._merge_arguments(args)

        # Save original arguments
        self.data['args'] = ' '.join(sys.argv)

        self.log.debug("Settings: %s", self.data)

    def _merge_arguments(self, args):
        """Merge environment variable with arguments in self.data.

        Note: arguments have higher precedence.

        :type args: dict
        :param args: Parsed arguments.
        """
        self.data.update(
            # Filter out None arguments
            filter(lambda x: x[1] or x[1] is False, args.items())
        )

    def _read_envars(self):
        """Read environment variables to self.data.
        """
        # Will raise an error if ECSDEPLOY_CONFIG environtment variable
        # is not set
        ecsdeploy_config = os.environ.get('ECSDEPLOY_CONFIG')
        assert ecsdeploy_config, ("Unable to read ECSDEPLOY_CONFIG "
                                  "environment variable.")
        self.data['ECSDEPLOY_CONFIG'] = ecsdeploy_config
