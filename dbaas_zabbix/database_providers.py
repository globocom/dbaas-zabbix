# -*- coding: utf-8 -*-
from dbaas_zabbix.provider import ZabbixProvider
import logging

LOG = logging.getLogger(__name__)


class DatabaseZabbixProvider(ZabbixProvider):

    def __init__(self, dbaas_api, zabbix_api):
        super(DatabaseZabbixProvider, self).__init__(dbaas_api, zabbix_api)
        self.main_clientgroup = self.main_clientgroup
        self.extra_clientgroup = self.extra_clientgroup

    def create_basic_monitors(self, ):
        clientgroup = self.main_clientgroup
        for host in self.hosts:
            self._create_basic_monitors(
                host=host.hostname, ip=host.address, clientgroup=clientgroup,
                alarm="group", **self.get_basic_monitors_extra_parameters()
            )

    def get_client_groups(self,):
        clientgroup = []
        if self.main_clientgroup:
            clientgroup.append(self.main_clientgroup)
        if self.extra_clientgroup:
            clientgroup.append(self.extra_clientgroup)

        return clientgroup

    def get_basic_monitors_extra_parameters(self):
        return self.extra_parameters('create_basic_monitors')

    def get_database_monitors_extra_parameters(self):
        return self.extra_parameters('create_database_monitors')

    def delete_basic_monitors(self, ):
        for host in self.hosts:
            self._delete_monitors(host=host.hostname)

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self,):
        for zabbix_host in self.get_zabbix_databases_hosts():
            self._delete_monitors(host=zabbix_host)

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = []

        for instance in self.instances:
            zabbix_hosts.append(instance.dns)

        for instance in self.secondary_ips:
            zabbix_hosts.append(instance.dns)

        return zabbix_hosts

    def disable_alarms(self,):
        for host in self.hosts:
            self._disable_alarms(host=host.hostname)

        for database_host in self.get_zabbix_databases_hosts():
            self._disable_alarms(host=database_host)

    def enable_alarms(self,):
        for host in self.hosts:
            self._enable_alarms(host=host.hostname)

        for database_host in self.get_zabbix_databases_hosts():
            self._enable_alarms(host=database_host)

    def update_host_interface(self, host_name, **kwargs):
        host_id = self.get_host_id(host_name)
        interface_id = self.get_host_interface_id(host_id)
        return self._update_host_interface(interfaceid=interface_id, **kwargs)


class MySQLSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = False
    __version__ = ['5.6.15', '5.6.24', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.instances:
            self._create_database_monitors(
                host=instance.dns, dbtype='mysql', alarm='group',
                clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters())


class MySQLHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True
    __version__ = ['5.6.15', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        extra_parameters = self.get_database_monitors_extra_parameters()
        for instance in self.database_instances:
            params = {'host': instance.dns,
                      'alarm': 'group',
                      'clientgroup': clientgroup,
                      'dbtype': 'mysql',
                      'healthcheck': {'host': instance.dns,
                                      'port': '80',
                                      'string': 'WORKING',
                                      'uri': 'health-check/'},
                      'healthcheck_monitor': {'host': instance.dns,
                                              'port': '80',
                                              'string': 'WORKING',
                                              'uri': 'health-check/monitor/'}}
            params.update(extra_parameters)
            self._create_database_monitors(**params)

        for instance in self.secondary_ips:
            self._create_database_monitors(
                host=instance.dns, dbtype='mysql',
                alarm='group', clientgroup=clientgroup, **extra_parameters)

    def migrate_database_monitors_flipper2fox(self, ):
        clientgroup = self.extra_clientgroup
        extra_parameters = self.get_database_monitors_extra_parameters()

        for instance in self.secondary_ips:
            self._delete_monitors(host=instance.dns)

        self._create_database_monitors(
            host=self.mysql_infra_dns_from_endpoint_dns, dbtype='mysql',
            alarm='group', clientgroup=clientgroup, **extra_parameters)

    def migrate_database_monitors_fox2flipper(self, ):
        clientgroup = self.extra_clientgroup
        extra_parameters = self.get_database_monitors_extra_parameters()

        self._delete_monitors(host=self.mysql_infra_dns_from_endpoint_dns)

        for instance in self.secondary_ips:
            self._create_database_monitors(
                host=instance.dns, dbtype='mysql',
                alarm='group', clientgroup=clientgroup, **extra_parameters)


class MySQLFoxHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True
    __version__ = ['5.6.24', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        extra_parameters = self.get_database_monitors_extra_parameters()
        for instance in self.database_instances:
            params = {'host': instance.dns,
                      'alarm': 'group',
                      'clientgroup': clientgroup,
                      'dbtype': 'mysql',
                      'healthcheck': {'host': instance.dns,
                                      'port': '80',
                                      'string': 'WORKING',
                                      'uri': 'health-check/'},
                      'healthcheck_monitor': {'host': instance.dns,
                                              'port': '80',
                                              'string': 'WORKING',
                                              'uri': 'health-check/monitor/'}}
            params.update(extra_parameters)
            self._create_database_monitors(**params)

        self._create_database_monitors(
            host=self.mysql_infra_dns_from_endpoint_dns, dbtype='mysql',
            alarm='group', clientgroup=clientgroup, **extra_parameters)

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = super(MySQLFoxHighAvailabilityZabbixProvider, self).get_zabbix_databases_hosts()
        zabbix_hosts.append(self.mysql_infra_dns_from_endpoint_dns)

        return zabbix_hosts


class MongoDBSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['2.4.10', ]

    def create_database_monitors(self):
        clientgroup = self.extra_clientgroup
        for instance in self.instances:
            self._create_database_monitors(
                host=instance.dns, dbtype='mongodb',
                alarm="group", clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters())


class MongoDBHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['2.4.10', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.database_instances:
            self._create_database_monitors(
                host=instance.dns, dbtype='mongodb',
                alarm="group", clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters())

        for instance in self.non_database_instances:
            self._create_database_monitors(
                host=instance.dns, dbtype='mongodb',
                alarm='group', clientgroup=clientgroup,
                arbiter='1', **self.get_database_monitors_extra_parameters())


class RedisZabbixProvider(DatabaseZabbixProvider):

    def get_web_monitors_extra_parameters(self,):
        return self.extra_parameters('create_web_monitors')

    def create_database_monitors(self,):
        clientgroup = self.get_client_groups()
        extra_parameters = self.get_web_monitors_extra_parameters()

        notes = self.alarm_notes
        params = {
            "notes": notes,
            "required_string": "WORKING",
            "alarm": "group",
            "clientgroup": clientgroup,
        }
        params.update(extra_parameters)

        hc_url = "http://{}:80"
        for instance in self.database_instances:
            custom_hc_url = hc_url.format(instance.dns)

            params["url"] = "{}/health-check/redis-con/".format(custom_hc_url)
            self._create_web_monitors(**params)

            params["url"] = "{}/health-check/redis-mem/".format(custom_hc_url)
            self._create_web_monitors(**params)

        for instance in self.non_database_instances:
            custom_hc_url = hc_url.format(instance.dns)
            params["url"] = "{}/health-check/sentinel-con/".format(
                custom_hc_url
            )
            self._create_web_monitors(**params)

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = []
        suffix = ':80/health-check/'

        for instance in self.database_instances:
            host = "web_{}{}redis-con/".format(instance.dns, suffix)
            zabbix_hosts.append(host)
            host = "web_{}{}redis-mem/".format(instance.dns, suffix)
            zabbix_hosts.append(host)

        for instance in self.non_database_instances:
            host = "web_{}{}sentinel-con/".format(instance.dns, suffix)
            zabbix_hosts.append(host)

        return zabbix_hosts


class RedisSingleZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = False
    __version__ = ['2.8.17', ]


class RedisHighAvailabilityZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = True
    __version__ = ['2.8.17', ]


class MongoDBThreeDotZeroSingleZabbixProvider(MongoDBSingleZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['3.0.12', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.database_instances:
            self._create_mongo_three_monitors(
                host=instance.dns, alarm="group",
                replicaset="0", clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters()
            )


class MongoDBThreeDotZeroHighAvailabilityZabbixProvider(
    DatabaseZabbixProvider
):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['3.0.12', ]

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.database_instances:
            self._create_mongo_three_monitors(
                host=instance.dns, alarm="group",
                replicaset="1", clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters()
            )

        clientgroup = self.get_client_groups()
        for instance in self.non_database_instances:
            self._create_tcp_monitors(
                host=instance.dns, port=str(instance.port), alarm='group',
                clientgroup=clientgroup,
                **self.get_database_monitors_extra_parameters()
            )

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = []
        zabbix_hosts.extend((instance.dns for instance in self.database_instances))

        for instance in self.non_database_instances:
            host = "tcp_{}-{}".format(instance.dns, instance.port)
            zabbix_hosts.append(host)

        return zabbix_hosts


class FakeSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = False
    __version__ = ['0.0.0', ]

    def create_database_monitors(self, alarm='group'):
        instances = self.instances
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)


class FakeHAZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = True
    __version__ = ['1.1.1', ]

    def create_database_monitors(self, alarm='group'):
        instances = self.instances
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)
