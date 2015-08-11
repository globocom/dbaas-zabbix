# -*- coding: utf-8 -*-
from provider import ZabbixProvider
import logging

LOG = logging.getLogger(__name__)


class MySQLSingleZabbixProvider(ZabbixProvider):
    def create_database_monitors(self,):
        self._create_database_monitors(dbtype='mysql', alarm='no')


class MySQLHighAvailabilityZabbixProvider(ZabbixProvider):
    def get_params_for_instance(self, instance, **kwargs):
        host = instance.dns
        kwargs['host'] = host

        if kwargs.get('healthcheck', d=None):
            kwargs['healthcheck']['host'] = host
            kwargs['healthcheck_monitor']['host'] = host

        return kwargs

    def create_database_monitors(self, alarm='yes'):
        instances = self.get_database_instances()
        params = {'dbtype': 'mysql', 'alarm': 'yes', 'arbiter': 0,
                  'healthcheck': {'port': '80', 'string': 'WORKING',
                                  'uri': 'health-check/'
                                  },
                  'healthcheck_monitor': {'port': '80', 'string': 'WORKING',
                                          'uri': 'health-check/monitor/'
                                          }
                  }

        self._create_database_monitors(instances, alarm=alarm, **params)

        del params['healthcheck']
        del params['healthcheck_monitor']

        instances = self.get_databaseinfra_secondary_ips()
        self.__create_database_monitors(instances, **params)


class MongoDBSingleZabbixProvider(ZabbixProvider):
    def create_database_monitors(self, alarm='yes'):
        self._create_database_monitors(dbtype='mongodb', alarm=alarm)


class MongoDBHighAvailabilityZabbixProvider(ZabbixProvider):
    def create_database_monitors(self, alarm='yes'):
        instances = self.get_database_instances()
        self._create_database_monitors(instances, dbtype='mongodb',
                                       alarm='yes')

        instances = self.get_non_database_instances()
        self._create_database_monitors(instances, dbtype='mongodb',
                                       alarm='yes', arbiter=1)


class RedisZabbixProvider(ZabbixProvider):
    def get_params_for_instance(self, instance, **kwargs):
        monitor_type = kwargs['monitor_type']
        del kwargs['monitor_type']

        kwargs = {"address": instance.dns,
                  "uri": "/health-check/{}/".format(monitor_type),
                  "var": monitor_type,
                  "notes": self.get_databaseifra_name()
                  }
        return kwargs


class RedisSingleZabbixProvider(RedisZabbixProvider):
    def create_database_monitors(self, alarm='yes'):
        instances = self.get_database_instances()
        self._create_web_monitors(monitor_type='redis-con',
                                  instances=instances, regexp='WORKING',
                                  alarm=alarm)

        self._create_web_monitors(monitor_type='redis-mem',
                                  instances=instances, regexp='WORKING',
                                  alarm=alarm)


class RedisHighAvailabilityZabbixProvider(ZabbixProvider):
    def create_database_monitors(self, alarm='yes'):
        instances = self.get_database_instances()

        self._create_web_monitors(monitor_type=['redis-mem', 'redis-con'],
                                  instances=instances, regexp='WORKING',
                                  alarm=alarm)

        instances = self.get_non_database_instances()
        self._create_web_monitors(instances=instances, regexp='WORKING',
                                  monitor_type=['sentinel-con'], alarm=alarm
                                  )
