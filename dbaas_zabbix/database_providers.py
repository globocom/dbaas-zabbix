# -*- coding: utf-8 -*-
from dbaas_zabbix.provider import ZabbixProvider
from dbaas_zabbix.custom_exceptions import NotImplementedError
import logging

LOG = logging.getLogger(__name__)


class DatabaseZabbixProvider(ZabbixProvider):
    def create_basic_monitors(self, ):
        for host in self.get_hosts():
            self._create_basic_monitors(host=host.hostname,
                                        ip=host.address,
                                        clientgroup=self.clientgroup,
                                        alarm="group"
                                        )

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
        for instance in self.get_all_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mysql',
                                           alarm='group')


class MySQLHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True

    def create_database_monitors(self,):
        for instance in self.get_database_instances():
            params = {'host': instance.dns,
                      'alarm': 'yes',
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
                                           alarm='yes')


class MongoDBSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False

    def create_database_monitors(self):
        for instance in self.get_all_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm="group")


class MongoDBHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = True

    def create_database_monitors(self,):
        for instance in self.get_database_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm="yes")

        for instance in self.get_non_database_instances():
            self._create_database_monitors(host=instance.dns,
                                           dbtype='mongodb',
                                           alarm='yes',
                                           arbiter='1')


class RedisZabbixProvider(DatabaseZabbixProvider):

    def create_database_monitors(self,):

        if self.__is_ha__:
            alarm = "yes"
        else:
            alarm = "group"
        params = {
            "notes": self.get_databaseifra_name(),
            "regexp": "WORKING",
            "alarm": alarm,
            "clientgroup": self.clientgroup,
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
