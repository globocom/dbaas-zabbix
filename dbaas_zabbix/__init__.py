#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from dbaas_zabbix.provider_factory import ProviderFactory
from pyzabbix import ZabbixAPI


def factory_for(**kwargs):
    databaseinfra = kwargs['databaseinfra']
    credentials = kwargs['credentials']
    del kwargs['databaseinfra']
    del kwargs['credentials']

    dbaas_api = DatabaseAsAServiceApi(databaseinfra, credentials)

    return ProviderFactory(dbaas_api, zabbix_api=ZabbixAPI, **kwargs)
