# -*- coding: utf-8 -*-
import logging
from dbaas_zabbix.custom_exceptions import NotImplementedError

LOG = logging.getLogger(__name__)


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra):
        self.databaseinfra = databaseinfra
        self.driver = self.get_databaseinfra_driver()
        self.database_instances = self.get_database_instances()

    def get_all_instances(self, ):
        return self.databaseinfra.instances.all()

    def get_databaseinfra_driver(self):
        return self.databaseinfra.get_driver()

    def get_database_instances(self):
        return self.driver.get_database_instances()

    def get_non_database_instances(self,):
        return self.driver.get_non_database_instances()

    def get_hosts(self,):
        instances = self.driver.get_database_instances()
        return [instance.hostname for instance in instances]

    def get_environment(self):
        return self.databaseinfra.environment

    def get_databaseifra_name(self):
        return self.databaseinfra.name

    def get_databaseinfra_secondary_ips(self):
        return self.databaseinfra.cs_dbinfra_attributes.all()


class ZabbixProvider(DatabaseAsAServiceApi):

    def __init__(self, user, password, endpoint, clientgroups, databaseinfra,
                 api_class):
        super(ZabbixProvider, self).__init__(databaseinfra,)

        self.environment = self.get_environment()
        self.clientgroups = clientgroups
        self.api = api_class(endpoint)
        self.api.login(user=user, password=password)
        self.databaseinfra = databaseinfra

    def __create_basic_monitors(self, params):
        return self.api.globo.createBasicMonitors(params)

    def __create_database_monitors(self, params):
        LOG.info("Creating databse monitor with params: {}".format(params))
        return self.api.globo.createDBMonitors(params=params)

    def __create_web_monitors(self, params):
        return self.api.globo.createWebMonitors(params=params)

    def __delete_monitors(self, params):
        return self.api.globo.deleteMonitors(params)

    def _create_basic_monitors(self,):
        for host in self.get_hosts():
            LOG.info("Creating basic monitor for host: {}".format(host))
            groups = self.clientgroups
            self.__create_basic_monitors(params={"host": host.hostname,
                                                 "ip": host.address,
                                                 "clientgroup": groups})

    def _delete_basic_monitors(self,):
        for host in self.get_hosts():
            LOG.info("Destroying basic monitor for host: {}".format(host))
            self.__delete_monitors(params={"host": host.hostname})

    def _delete_database_monitors(self, instances):
        for instance in instances:
            msg = "Destroying database monitor for host: {}"
            LOG.info(msg.format(instance))
            self.__delete_monitors(params={"host": instance.dns})

    def create_database_monitors(self, ):
        raise NotImplementedError

    def delete_database_monitors(self, ):
        raise NotImplementedError
