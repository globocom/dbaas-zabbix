# -*- coding: utf-8 -*-
import logging
from dbaas_zabbix.custom_exceptions import NotImplementedError

LOG = logging.getLogger(__name__)


class ZabbixProvider(object):
    __provider_name__ = None
    __is_ha__ = None

    def __init__(self, dbaas_api, zabbix_api):
        self.dbaas_api = dbaas_api
        self.api = zabbix_api(dbaas_api.get_credential_endpoint())
        self.api.login(user=dbaas_api.get_credential_user(),
                       password=dbaas_api.get_credential_password())

    def __getattr__(self, name):
        if name.startswith('get_'):
            return getattr(self.dbaas_api, name)

    def _delete_monitors(self, host):
        LOG.info("Destroying monitor for host: {}".format(host))
        return self.api.globo.deleteMonitors(host)

    def _create_basic_monitors(self, **kwargs):
        LOG.info("Creating basic monitor with params: {}".format(kwargs))
        return self.api.globo.createBasicMonitors(**kwargs)

    def _create_database_monitors(self, **kwargs):
        LOG.info("Creating databse monitor with params: {}".format(kwargs))
        return self.api.globo.createDBMonitors(**kwargs)

    def _create_web_monitors(self, **kwargs):
        LOG.info("Creating web monitor with params: {}".format(kwargs))
        return self.api.globo.createWebMonitors(**kwargs)

    def _get_host_info(self, **kwargs):
        return self.api.host.get(**kwargs)

    def _update_host_info(self, **kwargs):
        return self.api.host.update(**kwargs)

    def _get_host_group_info(self, **kwargs):
        return self.api.hostgroup.get(**kwargs)

    def create_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self, **kwargs):
        raise NotImplementedError
