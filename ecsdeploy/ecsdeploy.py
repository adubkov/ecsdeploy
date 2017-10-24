import logging
import sys

import boto3

from botocore.config import Config

from .args import Arguments
from .config import Config
from .cluster import Cluster
from .logger import Logger
from .service import Service
from .settings import Settings
from .task_definition import TaskDefinition
from .exceptions import ECSDeployException

class ECSDeploy(object):
    def __init__(self, args=None, path=None):
        self.args = Arguments(args)
        self.settings = Settings(self.args)
        debug = logging.DEBUG if self.settings.get('debug') else logging.INFO
        self.log = Logger(name=__name__, log_level=debug)
        self.path = path if path else self.settings.get('ECSDEPLOY_CONFIG')

        self.config = Config(
                self.settings['ECSDEPLOY_CONFIG'],
                self.settings['environment'],
                self.settings['region'],
                self.settings['service'],
                self.settings['tag'],
                self.args['var'],
                self.args['cfg'],
        )

        # aws service connections
        self.conn = dict(
            ecs=self._get_aws_client('ecs', self.settings)
        )

    def start(self):
        if self.args['print']:
            print(self.config)
            return

        cluster = self._create_cluster()
        if not cluster:
            raise ECSDeployException("Could not get or create cluster. "
                "Please vefiry your account permissions and limits for ECS.")

        task_definition = self._register_task_definition()
        if not task_definition:
            raise ECSDeployException("Could not get or create task definition.")

        service = self._create_or_update_service(task_definition)
        if not service:
            raise ECSDeployException("Could not create or update service.")

        if self.args['verify']:
            self.log.info("Waiting for service update will completed.")
        elif service['taskDefinition'] == task_definition['taskDefinitionArn']:
            self.log.info("Service '%s', Task definition '%s:%s'. UPDATED",
                service['serviceName'], task_definition['family'], task_definition['revision'])

    def _get_aws_client(self, aws_service, s):
        """
        Credentials lookup order:
        1. Use credentials
        2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
            AWS_SESSION_TOKEN)
        3. Use aws profile from shared credential file (~/.aws/credentials)
        4. AWS config file (~/.aws/config)
        5. Assume Role provider
        6. Boto2 config file (/etc/boto.cfg and ~/.boto)
        7. Instance metadata with IAM Role
        """

        config = Config(
            retries = dict(
                max_attempts = 50
            )
        )

        session = boto3.session.Session(
            region_name=s['region'],
            profile_name=s.get('aws_profile')
        )

        return session.client(aws_service, config=config)

    def _create_cluster(self):
        ecs = self.conn['ecs']
        cluster_name = self.config['service']['cluster']
        region_name = self.settings['region']
        cluster = Cluster(ecs, region_name, cluster_name)
        res = cluster.get()
        return res if res else cluster.create()

    def _register_task_definition(self):
        ecs = self.conn['ecs']
        cluster_name = self.config['service']['cluster']
        task_definition = TaskDefinition(ecs, self.config)

        revision = self.args['revision']
        if revision:
            res = task_definition.get(revision)
        else:
            res = task_definition.register()

        return res

    def _create_or_update_service(self, task_definition=None):
        ecs = self.conn['ecs']
        service = Service(ecs, self.config, task_definition)

        res = service.get()
        if not res:
            res = service.create()
        else:
            task_definition_arn = res['taskDefinition']
            if task_definition_arn == task_definition['taskDefinitionArn']:
                task_definition_name = task_definition_arn.split('/')[1]
                self.log.info("Service '%s' already updated to '%s'.",
                    self.config['service']['name'], task_definition_name)
                return res
            res = service.update()

        return res


def main():
    logging.getLogger("boto").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)

    ecsdeploy = ECSDeploy()
    ecsdeploy.start()
