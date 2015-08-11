# -*- coding: utf-8 -*-
import logging
from dbaas_zabbix.custom_exceptions import NotImplementedError

LOG = logging.getLogger(__name__)


class ZabbixProvider(object):
    def __init__(self, user, password, endpoint, clientgroups, dbaas_api,
                 zabbix_api):
        self.dbaas_api = dbaas_api
        self.clientgroups = clientgroups
        self.api = zabbix_api(endpoint)
        self.api.login(user=user, password=password)

    def __getattr__(self, name):
        if name.startswith('get_'):
            return getattr(self.dbaas_api, name)

    def __create_basic_monitors(self, **kwargs):
        return self.api.globo.createBasicMonitors(**kwargs)

    def __create_database_monitors(self, **kwargs):
        LOG.info("Creating databse monitor with params: {}".format(kwargs))
        return self.api.globo.createDBMonitors(**kwargs)

    def __create_web_monitors(self, **kwargs):
        return self.api.globo.createWebMonitors(**kwargs)

    def __delete_monitors(self, host):
        return self.api.globo.deleteMonitors(host)

    def _create_basic_monitors(self, hosts, **kwargs):
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
            params = self.get_params_for_instance(instance, **kwargs)
            self.__create_database_monitors(**params)

    def _create_web_monitors(self, instances, **kwargs):
        for instance in instances:
            params = self.get_params_for_instance(instance, **kwargs)
            self.__create_web_monitors(**params)

    def create_basic_monitors(self, **kwargs):
        hosts = self.get_hosts()
        self._create_basic_monitors(hosts, **kwargs)

    def delete_basic_monitors(self,):
        hosts = self.get_hosts()
        self._delete_basic_monitors(hosts)

    def get_params_for_instance(self, instance, **kwargs):
        host = instance.dns
        kwargs['host'] = host
        return kwargs

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self, **kwargs):
        raise NotImplementedError
