# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)


class ZabbixProvider(object):
    __provider_name__ = None
    __is_ha__ = None
    __version__ = None

    def __init__(self, dbaas_api, zabbix_api):
        self.dbaas_api = dbaas_api
        self.api = zabbix_api(dbaas_api.endpoint)
        self.api.login(user=dbaas_api.user, password=dbaas_api.password)

    def __getattr__(self, name):
        return getattr(self.dbaas_api, name)

    def _delete_monitors(self, host):
        LOG.info("Destroying monitor for host: {}".format(host))
        return self.api.globo.deleteMonitors(host)

    def _create_basic_monitors(self, **kwargs):
        LOG.info("Creating basic monitor with params: {}".format(kwargs))
        return self.api.globo.createBasicMonitors(**kwargs)

    def _create_database_monitors(self, **kwargs):
        LOG.info("Creating database monitor with params: {}".format(kwargs))
        return self.api.globo.createDBMonitors(**kwargs)

    def _create_mongo_three_monitors(self, **kwargs):
        LOG.info("Creating mongo3 monitor with params: {}".format(kwargs))
        return self.api.globo.createMongo3Monitors(**kwargs)

    def _create_web_monitors(self, **kwargs):
        LOG.info("Creating web monitor with params: {}".format(kwargs))
        return self.api.globo.createWebMonitors(**kwargs)

    def _get_host_info(self, **kwargs):
        return self.api.host.get(**kwargs)

    def _update_host_interface(self, **kwargs):
        return self.api.hostinterface.update(**kwargs)

    def _get_host_interface(self, **kwargs):
        return self.api.hostinterface.get(**kwargs)

    def _update_host_info(self, **kwargs):
        return self.api.host.update(**kwargs)

    def _get_host_group_info(self, **kwargs):
        return self.api.hostgroup.get(**kwargs)

    def _disable_alarms(self, **kwargs):
        return self.api.globo.disableAlarms(**kwargs)

    def _enable_alarms(self, **kwargs):
        return self.api.globo.enableAlarms(**kwargs)

    def get_host_id(self, host_name):
        host_info = self._get_host_info(search={'name': host_name})
        return host_info[0]['hostid']

    def get_host_interface_id(self, host_id):
        host_interface = self.api.hostinterface.get(hostids=host_id)
        return host_interface[0]['interfaceid']

    def create_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self, **kwargs):
        raise NotImplementedError

    def update_host_interface(self, **kwargs):
        raise NotImplementedError
