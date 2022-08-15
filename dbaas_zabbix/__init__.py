#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys

from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from dbaas_zabbix.provider_factory import ProviderFactory
from pyzabbix import ZabbixAPI

LOG = logging.getLogger(__name__)


def set_integration_logger():
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)


def factory_for(**kwargs):
    databaseinfra = kwargs['databaseinfra']
    credentials = kwargs['credentials']
    del kwargs['databaseinfra']
    del kwargs['credentials']

    zabbix_api = ZabbixAPI
    if kwargs.get('zabbix_api'):
        zabbix_api = kwargs.get('zabbix_api')
        del kwargs['zabbix_api']

    dbaas_api = DatabaseAsAServiceApi(databaseinfra, credentials)

    return ProviderFactory.factory(dbaas_api, zabbix_api=zabbix_api, **kwargs)


ZABBIX_INTEGRATION_LOG = os.getenv('ZABBIX_INTEGRATION_LOG') == "1"
LOG.info('ZABBIX_INTEGRATION_LOG = ' + str(ZABBIX_INTEGRATION_LOG))
if ZABBIX_INTEGRATION_LOG:
    LOG.info("Activating log stream for pyzabbix")
    set_integration_logger()
