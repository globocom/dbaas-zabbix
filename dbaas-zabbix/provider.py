#!/usr/bin/env python
# -*- coding: utf-8 -*-
from zabbix_api import ZabbixAPI
from physical.models import DatabaseInfra
import logging

LOG = logging.getLogger(__name__)

class ZabbixProvider(object):
    
    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        from dbaas_credentials.credential import Credential
        from dbaas_credentials.models import CredentialType
        integration = CredentialType.objects.get(type= CredentialType.ZABBIX)
        return Credential.get_credentials(environment= environment, integration= integration)
    
    @classmethod
    def auth(self, dbinfra): 
        credentials = self.get_credentials(environment = dbinfra.environment)

        zapi = ZabbixAPI(server=credentials.endpoint, path="", log_level=6)
        zapi.login(credentials.user, credentials.password)
        return zapi

    @classmethod
    def create_monitoring(self, dbinfra):
        if isinstance(dbinfra, DatabaseInfra):
            zapi = self.auth(dbinfra=dbinfra)
            LOG.info("Creating zabbix monitoring...")
            zapi.globo.createDBMonitors({"name" : dbinfra.name, "host" : dbinfra.endpoint, "dbtype" : "mysql"})

    @classmethod
    def destroy_monitoring(self, dbinfra):
        if isinstance(dbinfra, DatabaseInfra):
        	LOG.info("Destroying zabbix monitoring...")
        	zapi = self.auth(dbinfra=dbinfra)
        	zapi.globo.deleteMonitors({"host":dbinfra.name,})