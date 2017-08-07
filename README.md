# ECSDeploy

When you using ecsdeploy you have to be in current configs directory:
```
$ tree ~/ecsdeploy
.
├── config
└── services
    └── webapp
```

Also you can use `ECSDEPLOY_CONFIG` environment variable to specify the path to ecsdeploy configs:

```
cat >> ~/.bash_profile <<EOF
export ECSDEPLOY_CONFIG=~/ecsdeploy
EOF
```

## Configuration

**~/ecsdeploy/config**:
```
ecr:
  uri: 1234567890.dkr.ecr.us-west-1.amazonaws.com
role: ecsServiceRole
namespace: release
```

### Simple config example

**~/ecsdeploy/services/webapp**:
```
service:
  name: elasticsearch
  deployment:
    maximum_percent: 100
    minimum_healthy_percent: 0
  desired_count: 1

task:
  volumes:
    config: /etc/elasticsearch
    data: /data
    logs: /var/log/elasticsearch

  containers:
    elasticsearch:
      image: elasticsearch:5
      memory: 2048
      essential: True
      port_mappings:
        -
          host_port: 0
          container_port: 9200
          protocol: tcp
      mount_points:
        /usr/share/elasticsearch/config:
          source_volume: config
        /usr/share/elasticsearch/data:
          source_volume: db
        /usr/share/elasticsearch/logs:
          source_volume: logs

environments:
  prd:
    namespace: release
    service:
      cluster: prd-ecs-cluster
```

### Usage

#### Variables
You can use varibales inside configs and pass them from command line. 
Variables injection will happen on pre-processing configuration, and therefore it is very powerful feature.

Create: `~/services/webapp` file with following content:
```
service:
  name: helloworld 

task:
  containers:
    helloworld:
      essential: True

environments:
   {{ environment }}: 
    service:
      cluster: {{ cluster }}
```

Passing variables:
```
$ ecsdeploy -e demo -r us-west-1 -s webapp -v cluster=webapp -v environment=demo --debug

2017-08-07 14:20:03 [DEBUG] ecsdeploy.config: Effective config:
ecr:
    uri: 1234567890.dkr.ecr.us-west-1.amazonaws.com
role: ecsServiceRole
service:
    cluster: webapp
    name: helloworld
task:
    containers:
        helloworld:
            environment_variables: {}
            essential: true
            image: 1234567890.dkr.ecr.us-west-1.amazonaws.com/release/helloworld:latest
            namespace: release
```

#### Configuration override

Lets say we want change name of service from `helloworld` to `hellobuddy`.

```
$ ecsdeploy -e demo -r us-west-1 -s service_config -c service.name=hellobuddy --debug

2017-08-07 14:21:39 [DEBUG] ecsdeploy.config: Effective config:
ecr:
    uri: 1234567890.dkr.ecr.us-west-1.amazonaws.com
role: ecsServiceRole
service:
    cluster: webapp
    name: helloboddy
task:
    containers:
        helloworld:
            environment_variables: {}
            essential: true
            image: 1234567890.dkr.ecr.us-west-1.amazonaws.com/release/helloworld:latest
            namespace: release
```

### Tests

To run tests:
```
python setup.py test
```

To debug tests:
```
nosetests -x -s --pdb
```

To generate coverage report:
```
python3 setup.py nosetests --with-coverage --cover-erase --cover-package=ecsdeploy --cover-html
```
