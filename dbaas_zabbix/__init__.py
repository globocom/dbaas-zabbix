#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from dbaas_zabbix.provider_factory import ProviderFactory


def factory_for(**kwargs):
    databaseinfra = kwargs['databaseinfra']
    del kwargs['databaseinfra']

    dbaas_api = DatabaseAsAServiceApi(databaseinfra)

    return ProviderFactory(dbaas_api, **kwargs)
