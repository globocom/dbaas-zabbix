# -*- coding: utf-8 -*-
from dbaas_zabbix.provider import ZabbixProvider
import logging

LOG = logging.getLogger(__name__)


class DatabaseZabbixProvider(ZabbixProvider):

    def create_basic_monitors(self, ):
        for host in self.hosts:
            self.create_instance_basic_monitors(host)

    def create_instance_basic_monitors(self, host):
        self._create_basic_monitors(
            host=host.hostname, ip=host.address,
            alarm="yes", **self.get_basic_monitors_extra_parameters()
        )

    def get_basic_monitors_extra_parameters(self):
        return self.extra_parameters('create_basic_monitors')

    def get_database_monitors_extra_parameters(self):
        return self.extra_parameters('create_database_monitors')

    def delete_basic_monitors(self, ):
        for host in self.hosts:
            self.delete_instance_monitors(host_name=host.hostname)

    def delete_instance_monitors(self, host_name):
        self._delete_monitors(host=host_name)

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def create_instance_monitors(self, instance):
        raise NotImplementedError

    def delete_database_monitors(self,):
        for zabbix_host in self.get_zabbix_databases_hosts():
            self.delete_instance_monitors(host_name=zabbix_host)

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = []

        for instance in self.instances:
            zabbix_hosts.append(instance.dns)

        return zabbix_hosts

    def disable_alarms(self,):
        for host in self.hosts:
            if self.get_host_id(host.hostname):
                self.disable_alarms_to(host_name=host.hostname)

        for database_host in self.get_zabbix_databases_hosts():
            if self.get_host_id(database_host):
                self.disable_alarms_to(host_name=database_host)

    def enable_alarms(self,):
        for host in self.hosts:
            if self.get_host_id(host.hostname):
                self.enable_alarms_to(host_name=host.hostname)

        for database_host in self.get_zabbix_databases_hosts():
            if self.get_host_id(database_host):
                self.enable_alarms_to(host_name=database_host)

    def disable_alarms_to(self, host_name):
        return self._disable_alarms(host=host_name)

    def enable_alarms_to(self, host_name):
        return self._enable_alarms(host=host_name)

    def update_host_interface(self, host_name, **kwargs):
        host_id = self.get_host_id(host_name)
        interface_id = self.get_host_interface_id(host_id)
        return self._update_host_interface(interfaceid=interface_id, **kwargs)


class MySQLSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = False
    __version__ = ['5.6.15', '5.6.24', '5.6.40', '5.7.21', '5.7.25']

    def create_database_monitors(self,):
        for instance in self.instances:
            self.create_instance_monitors(instance)

    def create_instance_monitors(self, instance):
        self._create_database_monitors(
            host=instance.dns, dbtype='mysql', alarm='yes',
            **self.get_database_monitors_extra_parameters()
        )


class MySQLHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True
    __version__ = ['5.6.15', '5.6.40']

    def create_database_monitors(self,):
        for instance in self.database_instances:
            self.create_instance_monitors(instance)

    def create_instance_monitors(self, instance):
        extra_parameters = self.get_database_monitors_extra_parameters()

        if instance in self.database_instances:
            params = {'host': instance.dns,
                      'alarm': 'yes',
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

    def migrate_database_monitors_flipper2fox(self, ):
        extra_parameters = self.get_database_monitors_extra_parameters()
        self._create_database_monitors(
            host=self.mysql_infra_dns_from_endpoint_dns, dbtype='mysql',
            alarm='yes', **extra_parameters
        )

    def migrate_database_monitors_fox2flipper(self, ):
        extra_parameters = self.get_database_monitors_extra_parameters()

        self.delete_instance_monitors(
            host_name=self.mysql_infra_dns_from_endpoint_dns
        )


class MySQLFoxHighAvailabilityZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mysql'
    __is_ha__ = True
    __version__ = ['5.6.24', '5.6.40', '5.7.21', '5.7.25']

    def create_database_monitors(self,):
        extra_parameters = self.get_database_monitors_extra_parameters()
        for instance in self.database_instances:
            self.create_instance_monitors(instance)

        self._create_database_monitors(
            host=self.mysql_infra_dns_from_endpoint_dns, dbtype='mysql',
            alarm='yes', **extra_parameters)

    def create_instance_monitors(self, instance):
        extra_parameters = self.get_database_monitors_extra_parameters()
        params = {'host': instance.dns,
                  'alarm': 'yes',
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

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = super(MySQLFoxHighAvailabilityZabbixProvider, self).get_zabbix_databases_hosts()
        zabbix_hosts.append(self.mysql_infra_dns_from_endpoint_dns)

        return zabbix_hosts


class RedisZabbixProvider(DatabaseZabbixProvider):

    def get_web_monitors_extra_parameters(self,):
        return self.extra_parameters('create_web_monitors')

    def create_database_monitors(self,):
        for instance in self.database_instances:
            self.create_instance_monitors(instance)

        for instance in self.non_database_instances:
            self.create_instance_monitors(instance)

    def create_instance_monitors(self, instance):
        extra_parameters = self.get_web_monitors_extra_parameters()
        hc_url = "http://{}:80"

        notes = self.alarm_notes
        params = {
            "notes": notes,
            "required_string": "WORKING",
            "alarm": "yes",
            "doc": notes,
            "project": "dbaas",
        }
        params.update(extra_parameters)

        if instance in self.database_instances:
            params["webserver"] = instance.dns
            custom_hc_url = hc_url.format(instance.dns)

            params["url"] = "{}/health-check/redis-con/".format(custom_hc_url)
            self._create_web_monitors(**params)

            params["url"] = "{}/health-check/redis-mem/".format(custom_hc_url)
            self._create_web_monitors(**params)

            self._create_redis_monitors(
                host=instance.dns, password=instance.databaseinfra.password,
                port=str(instance.port), alarm='yes', notes=notes,
                doc=notes, project="dbaas",
                **self.get_database_monitors_extra_parameters()
            )


        if instance in self.non_database_instances:
            params["webserver"] = instance.dns
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
            host = "redis_{}:{}_dbaas".format(instance.dns, instance.port)
            zabbix_hosts.append(host)

        for instance in self.non_database_instances:
            host = "web_{}{}sentinel-con/".format(instance.dns, suffix)
            zabbix_hosts.append(host)

        return zabbix_hosts


class RedisSingleZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = False
    __version__ = ['2.8.17', '3.2.6', '4.0.2']


class RedisHighAvailabilityZabbixProvider(RedisZabbixProvider):
    __provider_name__ = 'redis'
    __is_ha__ = True
    __version__ = ['2.8.17', '3.2.6', '4.0.2']


class MongoDBSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['2.4.10', ]

    def create_database_monitors(self,):
        for instance in self.database_instances:
            self.create_instance_monitors(instance)

        for instance in self.non_database_instances:
            self.create_instance_monitors(instance)

    def create_instance_monitors(self, instance):
        if instance in self.database_instances:
            self.create_mongodb_monitors(instance)
        elif instance in self.non_database_instances:
            self.create_arbiter_monitors(instance)

    def create_arbiter_monitors(self, instance):
        pass

    def create_mongodb_monitors(self, instance):
        self._create_database_monitors(
            host=instance.dns, dbtype='mongodb',
            alarm="yes", **self.get_database_monitors_extra_parameters()
        )


class MongoDBThreeDotZeroSingleZabbixProvider(MongoDBSingleZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['3.0.12', ]

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="0", **self.get_database_monitors_extra_parameters()
        )


class MongoDBThreeDotFourSingleZabbixProvider(MongoDBThreeDotZeroSingleZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['3.4.1', ]

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="0", mongo_version="3.4",
            **self.get_database_monitors_extra_parameters()
        )


class MongoDBFourDotZeroSingleZabbixProvider(MongoDBThreeDotFourSingleZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = False
    __version__ = ['4.0.3', ]

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="0", mongo_version="4.0",
            **self.get_database_monitors_extra_parameters()
        )


class MongoDBHighAvailabilityZabbixProvider(MongoDBSingleZabbixProvider):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['2.4.10', ]

    def create_arbiter_monitors(self, instance):
        self._create_database_monitors(
            host=instance.dns, dbtype='mongodb',
            alarm='yes', arbiter='1',
            **self.get_database_monitors_extra_parameters()
        )


class MongoDBThreeDotZeroHighAvailabilityZabbixProvider(
    MongoDBHighAvailabilityZabbixProvider
):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['3.0.12', ]

    def create_arbiter_monitors(self, instance):
        self._create_tcp_monitors(
            host=instance.dns, port=str(instance.port), alarm='yes',
            **self.get_database_monitors_extra_parameters()
        )

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="1", **self.get_database_monitors_extra_parameters()
        )

    def get_zabbix_databases_hosts(self,):
        zabbix_hosts = []
        zabbix_hosts.extend((instance.dns for instance in self.database_instances))

        for instance in self.non_database_instances:
            host = "tcp_{}-{}".format(instance.dns, instance.port)
            zabbix_hosts.append(host)

        return zabbix_hosts


class MongoDBThreeDotFourHighAvailabilityZabbixProvider(
    MongoDBThreeDotZeroHighAvailabilityZabbixProvider
):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['3.4.1', ]

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="1", mongo_version="3.4",
            **self.get_database_monitors_extra_parameters()
        )


class MongoDBFourDotZeroHighAvailabilityZabbixProvider(
    MongoDBThreeDotFourHighAvailabilityZabbixProvider
):
    __provider_name__ = 'mongodb'
    __is_ha__ = True
    __version__ = ['4.0.3', ]

    def create_mongodb_monitors(self, instance):
        self._create_mongo_three_monitors(
            host=instance.dns, alarm="yes", doc=self.alarm_notes,
            replicaset="1", mongo_version="4.0",
            **self.get_database_monitors_extra_parameters()
        )


class FakeSingleZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = False
    __version__ = ['0.0.0', ]

    def create_database_monitors(self, alarm='yes'):
        instances = self.instances
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)


class FakeHAZabbixProvider(DatabaseZabbixProvider):
    __provider_name__ = 'fake'
    __is_ha__ = True
    __version__ = ['1.1.1', ]

    def create_database_monitors(self, alarm='yes'):
        instances = self.instances
        self._create_database_monitors(instances, dbtype='fake', alarm=alarm)
