# -*- coding: utf-8 -*-
from provider import ZabbixProvider
import logging

LOG = logging.getLogger(__name__)


class MySQLSingleZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        self._create_database_monitors(dbtype='mysql', alarm='no')


class MySQLHighAvailabilityZabbixProvider(ZabbixProvider):
    def create_database_monitors(self, ):
        for instance in self.get_database_instances():
            params = {"host": instance.dns, "dbtype": 'mysql', "alarm": "yes",
                      "arbiter": 0, }
            params['healthcheck'] = {'host': instance.dns,
                                     'port': '80',
                                     'string': 'WORKING',
                                     'uri': 'health-check/',
                                     }
            params['healthcheck_monitor'] = {'host': instance.dns,
                                             'port': '80',
                                             'string': 'WORKING',
                                             'uri': 'health-check/monitor/',
                                             }

            self.__create_database_monitors(params)

        for secondary_ip in self.get_databaseinfra_secondary_ips():
            params = {"host": instance.dns, "dbtype": 'mysql', "alarm": "yes",
                      "arbiter": 0}

            self.__create_database_monitors(params)


class MongoDBSingleZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        self._create_database_monitors(dbtype='mongodb', alarm='no')


class MongoDBHighAvailabilityZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        self._create_database_monitors(dbtype='mongodb', alarm='yes')

        for arbiter in self.get_non_database_instances():
            params = {"host": arbiter.dns, "dbtype": 'mongodb', "alarm": "yes",
                      "arbiter": 1}
            self.__create_database_monitors(params)


class RedisSingleZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        instances = self.get_database_instances()
        self._create_web_monitors(monitor_type=['redis-mem', 'redis-con'],
                                  instances=instances, regexp='WORKING')


class RedisHighAvailabilityZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        instances = self.get_database_instances()
        self._create_web_monitors(monitor_type=['redis-mem', 'redis-con'],
                                  instances=instances, regexp='WORKING')

        instances = self.get_non_database_instances()
        self._create_web_monitors(instances=instances, regexp='WORKING',
                                  monitor_type=['sentinel-con']
                                  )
