import logging

from .utils import dict_map, dict_add

@dict_map
def make_load_balancer(m):
    lb = m[1]

    load_balancers_map = dict(
        targetGroupArn=lb.get('target_group_arn'),
        loadBalancerName=lb.get('load_balancer_name'),
        containerName=lb['container_name'],
        containerPort=lb['container_port'],
    )

    load_balancer = {}

    for k,v in load_balancers_map.items():
        dict_add(load_balancer, k, v)

    return load_balancer

class Service(object):
    def __init__(self, ecs, cfg, task_definition):
        self.log = logging.getLogger(__name__)
        self.ecs = ecs
        self.cfg = cfg
        self.service = self.cfg['service']
        self.cluster_name = self.service['cluster']
        self.service_name = self.service['name']
        self.task_definition = task_definition
        task_definition_family = self.task_definition['family']
        task_definition_revision = self.task_definition['revision']
        self.task_definition_name = '{family}:{revision}'.format(
            family=task_definition_family,
            revision=task_definition_revision
        )

    def get(self):
        services = [self.service_name]
        res = self.ecs.describe_services(cluster=self.cluster_name, services=services)
        active_services = list(filter(lambda x: x['status'] == 'ACTIVE', res['services']))
        return active_services[0] if active_services else {}

    def create(self):
        self.log.info("Cluster '%s', Service '%s', Task definition '%s'. CREATE",
            self.cluster_name,
            self.service_name,
            self.task_definition_name)

        service = self.service
        deployment = service['deployment']
        deployment_configuration=dict(
            # TODO: make default module with values
            maximumPercent=deployment.get('maximum_percent', '200'),
            minimumHealthyPercent=deployment.get('minimum_healthy_percent', '50'),
        )

        service_map = dict(
            cluster=self.cluster_name,
            serviceName=self.service_name,
            taskDefinition=self.task_definition_name,
            desiredCount=service['desired_count'],
            deploymentConfiguration=deployment_configuration,
            placementConstraints=service.get('placement_constraints', []),
            #  TODO: placement_strategy - convert dict to list of dicts
            placementStrategy=service.get('placement_strategy', [])
        )

        # TODO: Consider use aws naming convention for configs

        load_balancers = make_load_balancer(service.get('load_balancers', {}))

        # If you specify the role parameter, you must also specify a
        # load balancer object with the loadBalancers parameter.
        if load_balancers:
            service_map.update(dict(
                role=self.cfg['role'],
                loadBalancers=load_balancers,
            ))

        service = {}

        for k,v in service_map.items():
            dict_add(service, k, v)

        res = self.ecs.create_service(**service)

        return res['service']

    def update(self):
        self.log.info("Cluster '%s', Service '%s', Task definition '%s'. UPDATE",
            self.cluster_name,
            self.service_name,
            self.task_definition_name)

        service = self.service
        desired_count = service['desired_count']
        deployment = service['deployment']
        deployment_configuration=dict(
            maximumPercent=deployment['maximum_percent'],
            minimumHealthyPercent=deployment['minimum_healthy_percent'],
        )

        res = self.ecs.update_service(
            cluster=self.cluster_name,
            service=self.service_name,
            desiredCount=desired_count,
            taskDefinition=self.task_definition_name,
            deploymentConfiguration=deployment_configuration,
        )

        return res['service']
