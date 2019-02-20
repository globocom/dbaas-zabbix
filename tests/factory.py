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


class Team(object):
    def __init__(self, name):
        self.name = name

    @property
    def organization(self):
        return None


class Database(object):
    def __init__(self, name):
        self.name = name
        self.team = Team(name)

    def first(self):
        return self


class Driver(object):
    def __init__(self, databaseinfra):
        self.databaseinfra = databaseinfra

    def get_database_instances(self):
        return self.databaseinfra.instances

    def get_non_database_instances(self):
        return self.databaseinfra.instances


class CloudStackInfra(object):
    def all(self):
        return []


class DatabaseInfra(object):
    def __init__(self, instances, environment, plan, name):
        self.instances = instances
        self.environment = environment
        self.name = name
        self.engine = Engine(name)
        self.plan = plan
        self.cs_dbinfra_attributes = CloudStackInfra()
        self.databases = Database(name)

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
        self.triggers = []

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
        if method == 'host.get':
            request_json = [{'name': 'fake', 'hostid': '3309'}]
        elif method == 'hostinterface.get':
            request_json = [{'interfaceid': '3310'}]
        elif method == 'trigger.get':
            request_json = self.triggers

        return request_json

    def __getattr__(self, attr):
        return FakeZabbixAPIObjectClass(attr, self)

    def add_trigger(self, status, id):
        self.triggers.append({'status': str(status), 'triggerid': str(id)})


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

        @property
        def slack_notification(self):
            return None

        def get_parameter_by_name(self, name):
            if "slack_notification":
                return self.slack_notification

            return ''

        def get_parameters_by_group(self, group_name):
            if group_name == "group_host":
                return {
                    "support": "ZabbixSupport",
                    "grafana": "GrafanaTeam",
                    "graphite": "GraphiteGroup"
                }

            if group_name == "group_database":
                return {
                    "dbproduction": "DBA Team",
                    "grafana": "GrafanaTeam",
                    "dbaasmetrics": "DBaaS/Metrics"
                }

            return {}


class FakeCredentialWithSlack(FakeCredential):

        @property
        def slack_notification(self):
            return "@user,#channel"
