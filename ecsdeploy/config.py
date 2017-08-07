import logging
import os
import yaml

from jinja2 import Template

try:                                        # pytnon3
    from UserDict import UserDict
except ImportError:                         # python2
    from collections import UserDict

# TODO: Use default values for deployment and desired capacity
# TODO: Test if vars can be used in arguments (see readme)
# TODO: use default region from aws config by default

class Config(UserDict, object):
    def __init__(self, path, env, region_name, service_name, tag, pre_args=[], post_args=[]):
        self.log = logging.getLogger(__name__)
        self.tag = tag

        base_config_path = os.path.join(path, 'config')
        base_config = Config._load(base_config_path, pre_args)

        service_config_path = os.path.join(path, 'services', service_name)
        service_config = Config._load(service_config_path, pre_args)
        self.configs = [
            base_config,
            service_config,
        ]

        environments = self._generate_effective_config('environments')
        environment = environments[env]

        # Override config for region.
        if 'regions' in environment:
            region = environment['regions'][region_name]
        else:
            region = {}

        self.configs += [
            environments,
            environment,
            region,
        ]

        namespace = self._generate_effective_config('namespace')
        envvar = self._generate_effective_config('environment_variables')

        # Override env level
        service = self._generate_effective_config('service')
        task = self._generate_effective_config('task')

        effective_config = Config._merge_all([region, dict(service=service, task=task), service_config, base_config])

        for name, cfg in effective_config['task']['containers'].items():
            Config._generate_effective_container_config(cfg, envvar, 'environment_variables')
            Config._generate_effective_container_config(cfg, namespace, 'namespace')
            Config._generate_effective_container_image_uri(cfg,
                effective_config['ecr']['uri'],
                namespace,
                name,
                self.tag
            )

        self.data = self._post_processing(effective_config, post_args)

        self.log.debug("Effective config:\n%s", self.__repr__())

    def __repr__(self):
        return yaml.safe_dump(
            self.data,
            default_flow_style=False,
            allow_unicode=True,
            indent=4
        )

    @staticmethod
    def _merge(o1, o2):
        args = [o1,o2]

        if all(map(lambda x: isinstance(x, list), args)):
            return o1 + o2

        if not all(map(lambda x: isinstance(x, dict), args)):
            return o2 if o2 else o1

        r = o1.copy()
        for k, v in o2.items():
            if k not in r:
                r[k] = v
            elif isinstance(v, dict):
                r[k] = Config._merge(r[k], v)

        return r

    @staticmethod
    def _merge_all(args):
        result = {}
        for a in args:
            result = Config._merge(result, a)
        return result

    @staticmethod
    def _value_or_empty_dict(cfg, key):
        return cfg.pop(key) if key in cfg else {}

    def _generate_effective_config(self, key, configs=None):
        if configs is None:
            configs = self.configs

        values = []
        for cfg in configs:
            values += [ Config._value_or_empty_dict(cfg, key) ]

        return Config._merge_all(values)

    @staticmethod
    def _generate_effective_container_config(cfg, values, key):
        if not isinstance(cfg, (dict)):
            return
        cfg[key] = Config._merge(values, cfg.get(key, {}))

    @staticmethod
    def _generate_effective_container_image_uri(cfg, ecr, namespace, name, tag):
        # Do not override image url if it is specified.
        if cfg.get('image'):
            return

        image = '{ecr}/{namespace}/{name}:{tag}'.format(
            ecr=ecr,
            namespace=namespace,
            name=name,
            tag=tag)

        cfg['image'] = image

    @staticmethod
    def _read_file(path):
        with open(path, 'r') as f:
            data = f.read()
        return data

    @staticmethod
    def _pre_processing(content, args):
        template = Template(content)
        targs = [ tuple(x.split('=')) for x in args ]
        kwargs = dict((x,y) for x,y in targs)
        res = template.render(**kwargs)
        return res

    @staticmethod
    def _post_processing(config, args):
        for arg in args:
            k,v = arg.split('=')
            path = k.split('.')
            c = config
            for n, i in enumerate(path):
                if n == len(path) - 1:
                    c[i] = v
                    break
                else:
                    c = c[i]
        return config

    @staticmethod
    def _load(path, pre_args):
        content = Config._read_file(path)
        config = Config._pre_processing(content, pre_args)
        return yaml.load(config) if config else None
