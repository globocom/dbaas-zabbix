# -*- coding: utf-8 -*-
import logging
from dbaas_zabbix.custom_exceptions import NotImplementedError
from dbaas_api import DatabaseAsAServiceApi

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

    def __create_basic_monitors(self, **kwargs):
        return self.api.globo.createBasicMonitors(**kwargs)

    def __create_database_monitors(self, params):
        LOG.info("Creating databse monitor with params: {}".format(params))
        return self.api.globo.createDBMonitors(params=params)

    def __create_web_monitors(self, **kwargs):
        return self.api.globo.createWebMonitors(**kwargs)

    def __delete_monitors(self, host):
        return self.api.globo.deleteMonitors(host)

    def _create_basic_monitors(self, hosts):
        for host in hosts:
            LOG.info("Creating basic monitor for host: {}".format(host))
            self.__create_basic_monitors(host=host.hostname, ip=host.address,
                                         clientgroup=self.clientgroups)

    def _delete_basic_monitors(self, hosts):
        for host in hosts:
            LOG.info("Destroying basic monitor for host: {}".format(host))
            self.__delete_monitors(host=host.hostname)

    def _delete_database_monitors(self, instances):
        for instance in instances:
            msg = "Destroying database monitor for instance: {}"
            LOG.info(msg.format(instance))
            self.__delete_monitors(host=instance.dns)

    def _create_database_monitors(self, instances, **kwargs):
        for instance in instances:
            self.__create_database_monitors(host=instance.dns, **kwargs)

    def _create_web_monitors(self, instances, **kwargs):
        for instance in instances:
            self.__create_web_monitors(address=instance.dns, **kwargs)

    def create_basic_monitors(self,):
        hosts = self.get_hosts()
        self._create_basic_monitors(hosts)

    def delete_basic_monitors(self,):
        hosts = self.get_hosts()
        self._delete_basic_monitors(hosts)

    def create_database_monitors(self, ):
        raise NotImplementedError

    def delete_database_monitors(self, ):
        raise NotImplementedError
