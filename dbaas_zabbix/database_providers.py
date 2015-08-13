# -*- coding: utf-8 -*-
from dbaas_zabbix.provider import ZabbixProvider
from dbaas_zabbix.custom_exceptions import NotImplementedError
import logging

LOG = logging.getLogger(__name__)


class DatabaseZabbixProvider(ZabbixProvider):

    def __init__(self, dbaas_api, zabbix_api):
        super(DatabaseZabbixProvider, self).__init__(dbaas_api, zabbix_api)
        self.main_clientgroup = self.get_credential_main_clientgroup()
        self.extra_clientgroup = self.get_credential_extra_clientgroup()

    def create_basic_monitors(self, ):
        clientgroup = self.main_clientgroup
        for host in self.get_hosts():
            self._create_basic_monitors(host=host.hostname,
                                        ip=host.address,
                                        clientgroup=clientgroup,
                                        alarm="group")

    def delete_basic_monitors(self, ):
        for host in self.get_hosts():
            self._delete_monitors(host=host.hostname)

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self,):
        for instance in self.get_all_instances():
            self._delete_monitors(host=instance.dns)

        for instance in self.get_databaseinfra_secondary_ips():
            self._delete_monitors(host=instance.dns)


class MySQLSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = False

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.get_all_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mysql',
                                           alarm='group',
                                           clientgroup=clientgroup)


class MySQLHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.get_database_instances():
            params = {'host': instance.dns,
                      'alarm': 'group',
                      'clientgroup': clientgroup,
                      'dbtype': 'mysql',
                      'healthcheck': {'port': '80',
                                      'string': 'WORKING',
                                      'uri': 'health-check/'},
                      'healthcheck_monitor': {'port': '80',
                                              'string': 'WORKING',
                                              'uri': 'health-check/monitor/'}}

            self._create_database_monitors(**params)

        for instance in self.get_databaseinfra_secondary_ips():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mysql',
                                           alarm='group',
                                           clientgroup=clientgroup)


class MongoDBSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False

    def create_database_monitors(self):
        clientgroup = self.extra_clientgroup
        for instance in self.get_all_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm="group",
                                           clientgroup=clientgroup)


class MongoDBHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = True

    def create_database_monitors(self,):
        clientgroup = self.extra_clientgroup
        for instance in self.get_database_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm="group",
                                           clientgroup=clientgroup)

        for instance in self.get_non_database_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm='group',
                                           clientgroup=clientgroup,
                                           arbiter='1')


class RedisZabbixProvider(DatabaseZabbixProvider):

    def create_database_monitors(self,):
        clientgroup = []
        if self.main_clientgroup:
            clientgroup.append(self.main_clientgroup)
        if self.extra_clientgroup:
            clientgroup.append(self.extra_clientgroup)

        params = {
            "notes": self.get_databaseifra_name(),
            "regexp": "WORKING",
            "alarm": "group",
            "clientgroup": clientgroup,
        }
        for instance in self.get_database_instances():
            params["address"] = instance.dns
            params["var"] = "redis-con"
            params["uri"] = "/health-check/redis-con/"
            self._create_web_monitors(**params)

            params["var"] = "redis-mem"
            params["uri"] = "/health-check/redis-mem/"
            self._create_web_monitors(**params)

        for instance in self.get_non_database_instances():
            params["address"] = instance.dns
            params["var"] = "sentinel-con"
            params["uri"] = "/health-check/sentinel-con/"
            self._create_web_monitors(**params)

    def delete_database_monitors(self,):
        for instance in self.get_database_instances():
            host = "webmonitor_{}-80-redis-con".format(instance.dns)
            self._delete_monitors(host=host)
            host = "webmonitor_{}-80-redis-mem".format(instance.dns)
            self._delete_monitors(host=host)

        for instance in self.get_non_database_instances():
            host = "webmonitor_{}-80-sentinel-con".format(instance.dns)
            self._delete_monitors(host=host)


class RedisSingleZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = False


class RedisHighAvailabilityZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = True


class FakeSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = False

    def create_database_monitors(self, alarm='group'):
        instances = self.get_all_instances()
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)


class FakeHAZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = True

    def create_database_monitors(self, alarm='group'):
        instances = self.get_all_instances()
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)
