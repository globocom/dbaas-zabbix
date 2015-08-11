# -*- coding: utf-8 -*-
import logging
from dbaas_zabbix.custom_exceptions import NotImplementedError
from dbaas_api import DatabaseAsAServiceApi
from itertools import product

LOG = logging.getLogger(__name__)


class ZabbixProvider(DatabaseAsAServiceApi):

    def __init__(self, user, password, endpoint, clientgroups, databaseinfra,
                 api_class, alarm='yes'):
        super(ZabbixProvider, self).__init__(databaseinfra,)

        self.environment = self.get_environment()
        self.clientgroups = clientgroups
        self.api = api_class(endpoint)
        self.api.login(user=user, password=password)
        self.databaseinfra = databaseinfra
        self.alarm = alarm

    def __create_basic_monitors(self, params):
        return self.api.globo.createBasicMonitors(params)

    def __create_database_monitors(self, params):
        LOG.info("Creating databse monitor with params: {}".format(params))
        return self.api.globo.createDBMonitors(params=params)

    def __create_web_monitors(self, params):
        return self.api.globo.createWebMonitors(params=params)

    def __delete_monitors(self, params):
        return self.api.globo.deleteMonitors(params)

    def _create_basic_monitors(self):
        for host in self.get_hosts():
            LOG.info("Creating basic monitor for host: {}".format(host))
            groups = self.clientgroups
            self.__create_basic_monitors(params={"host": host.hostname,
                                                 "ip": host.address,
                                                 "clientgroup": groups})

    def _delete_basic_monitors(self):
        for host in self.get_hosts():
            LOG.info("Destroying basic monitor for host: {}".format(host))
            self.__delete_monitors(params={"host": host.hostname})

    def _delete_database_monitors(self, instances):
        for instance in instances:
            msg = "Destroying database monitor for host: {}"
            LOG.info(msg.format(instance))
            self.__delete_monitors(params={"host": instance.dns})

    def _create_database_monitors(self, dbtype, alarm=None):
        if alarm is None:
            alarm = self.alarm

        for instance in self.get_database_instances():
            params = {"host": instance.dns, "dbtype": dbtype, "alarm": alarm,
                      "arbiter": 0}
            self.__create_database_monitors(params)

    def _create_web_monitors(self, instances, monitor_types,
                             regexp='WORKING'):
        for instance, monitor_type in product(instances, monitor_types):
            params = {"address": instance.dns,
                      "port": "80",
                      "regexp": regexp,
                      "uri": "/health-check/{}/".format(monitor_type),
                      "var": "{}".format(monitor_type),
                      "alarm": "yes",
                      "notes": self.get_databaseifra_name,
                      "clientgroup": self.clientgroup,
                      }
            self.__create_web_monitors(params)

    def create_database_monitors(self, ):
        raise NotImplementedError

    def delete_database_monitors(self, ):
        raise NotImplementedError
