import logging

from .utils import dict_map, dict_add, int_or_none

@dict_map
def make_volumes(m):
    return dict(
        name=m[0],
        host=dict(
            sourcePath=m[1],
        ),
    )

@dict_map
def make_port_mapping(m):
    return dict(
        containerPort=int(m['container_port']),
        hostPort=int(m['host_port']),
        protocol=m['protocol'],
    )

@dict_map
def make_environment(m):
    return dict(
        name=m[0],
        value=str(m[1])
    )

@dict_map
def make_mount_points(m):
    res = {}
    containerPath = m[0]
    if containerPath:
        res['containerPath'] = containerPath

    sourceVolume = m[1]['source_volume']
    if sourceVolume:
        res['sourceVolume'] = sourceVolume

    readOnly=m[1].get('read_only')
    if readOnly:
        res['readOnly'] = bool(readOnly)

    return res

@dict_map
def make_volumes_from(m):
    res = {}
    sourceContainer = m[0]
    if sourceContainer:
        res['sourceContainer'] = sourceContainer

    readOnly = m[1].get('read_only')
    if readOnly:
        res['readOnly'] = bool(readOnly)

    return res

@dict_map
def make_extra_hosts(m):
    return dict(
        hostname=m[0],
        ipAddress=m[1]
    )

@dict_map
def make_ulimits(m):
    return dict(
        name=m[0],
        softLimit=int(m[1]['soft']),
        hardLimit=int(m[1]['hard'])
    )

def make_log_configuration(m):
    if not m:
        return None

    return dict(
        logDriver=m.get('log_driver', ''),
        options=m.get('options', {})
    )

@dict_map
def make_container(m):
    name = m[0]
    c = m[1]

    container_map = dict(
        name=name,
        image=c['image'],
        cpu=int_or_none(c.get('cpu')),
        memory=int_or_none(c.get('memory')),
        memoryReservation=int_or_none(c.get('memory_reservation')),
        links=c.get("links"),
        portMappings=make_port_mapping(c.get('port_mappings', {})),
        essential=c.get('essential'),
        entryPoint=c.get("entry_point"),
        command=c.get("command"),
        environment=make_environment(c.get('environment_variables', {})),
        mountPoints=make_mount_points(c.get('mount_points', {})),
        volumesFrom=make_volumes_from(c.get('volumes_from', {})),
        hostname=c.get('hostname'),
        user=c.get('user'),
        workingDirectory=c.get('working_directory'),
        disableNetworking=c.get('disable_networking'),
        privileged=c.get('privileged'),
        readonlyRootFilesystem=c.get('readonly_root_filesystem'),
        dnsServers=c.get('dns_servers'),
        dnsSearchDomains=c.get('dns_search_domains'),
        extraHosts=make_extra_hosts(c.get('extra_hosts', {})),
        dockerSecurityOptions=c.get('docker_security_options'),
        dockerLabels=c.get('docker_labels'),
        ulimits=make_ulimits(c.get('ulimits', {})),
        logConfiguration=make_log_configuration(c.get('log_configuration', {})),
    )

    container = {}

    for k,v in container_map.items():
        dict_add(container, k, v)

    return container

class TaskDefinition(object):
    def __init__(self, ecs, cfg):
        self.log = logging.getLogger(__name__)
        self.ecs = ecs
        self.cfg = cfg

    def get(self, revision):
        service = self.cfg['service']
        family = service['name']
        task_definition_name = ':'.join([family, revision])
        self.log.info("Task definition '%s'. GET", task_definition_name)
        res = self.ecs.describe_task_definition(taskDefinition=task_definition_name)
        return res['taskDefinition']

    def register(self):
        cfg = self.cfg
        service = cfg['service']
        task = cfg['task']
        containers = task['containers']

        self.log.info("Task definition '%s'. REGISTER", service['name'])

        container_definitions = make_container(containers)
        volumes = make_volumes(task.get('volumes', {}))
        placement_constraints = task.get('placement_constraints', [])

        res = self.ecs.register_task_definition(
            family=service['name'],
            taskRoleArn=task.get('task_role_arn', ''),
            networkMode=task.get('network_mode', 'bridge'),
            containerDefinitions=container_definitions,
            volumes=volumes,
            placementConstraints=placement_constraints,
        )

        return res['taskDefinition']
