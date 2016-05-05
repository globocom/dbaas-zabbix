from dbaas_zabbix.database_providers import DatabaseZabbixProvider


class Host(object):
    def __init__(self, address, dns):
        self.address = address
        self.hostname = dns


class Engine(object):
    def __init__(self, name, version='0.0.0'):
        self.engine_type = EngineType(name)
        self.version = version


class EngineType(object):
    def __init__(self, name):
        self.name = name


class Plan(object):
    def __init__(self, is_ha):
        self.is_ha = is_ha


class Instance(object):
    def __init__(self, dns, hostname):
        self.address = hostname.address
        self.dns = dns
        self.hostname = hostname


class Driver(object):
    def __init__(self, databaseinfra):
        self.databaseinfra = databaseinfra

    def get_database_instances(self):
        return self.databaseinfra.instances

    def get_non_database_instances(self):
        return self.databaseinfra.instances


class DatabaseInfra(object):
    def __init__(self, instances, environment, plan, name):
        self.instances = instances
        self.environment = environment
        self.name = name
        self.engine = Engine(name)
        self.plan = plan

    def get_driver(self):
        if hasattr(self, 'driver'):
            return self.driver

        self.driver = Driver(self)
        return self.driver


class InstanceList(list):
    def all(self):
        return self


def set_up_databaseinfra(is_ha=True, name="fake"):
    instances = InstanceList()
    plan = Plan(is_ha)
    for n in range(1, 4):
        address = '10.10.10.1{}'.format(n)
        dns = 'myhost_{}'.format(n)
        host = Host(address, dns + '.com')

        instance = Instance(dns + '.database.com', host)
        instances.append(instance)

    return DatabaseInfra(instances, 'development', plan, name)


class FakeZabbixAPI(object):
    def __init__(self, server,):
        self.server = server
        self.id = id(self)
        self.last_call = []

    def login(self, user, password):
        pass

    def do_request(self, method, params):
        request_json = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self.id,
        }
        self.last_call.append(request_json)
        return request_json

    def __getattr__(self, attr):
        return FakeZabbixAPIObjectClass(attr, self)


class FakeZabbixAPIObjectClass(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        def fn(*args, **kwargs):
            if args and kwargs:
                raise TypeError("Found both args and kwargs")
            return self.parent.do_request(
                '{0}.{1}'.format(self.name, attr),
                args or kwargs
            )
        return fn


class FakeDatabaseZabbixProvider(DatabaseZabbixProvider):
    @property
    def secondary_ips(self,):
        return []


class FakeCredential(object):
        def __init__(self):
            self.user = ''
            self.password = ''
            self.endpoint = ''

        def get_parameter_by_name(self, name):
            return ''

        def get_parameters_by_group(self, group_name):
            return {}
