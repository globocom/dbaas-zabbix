#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from dbaas_zabbix import provider_factory
from dbaas_zabbix import database_providers
from dbaas_zabbix import factory_for
from dbaas_zabbix.custom_exceptions import NotImplementedError
from tests import factory


class TestDatabaseAsAServiceApi(unittest.TestCase):
    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        self.dbaas_api = DatabaseAsAServiceApi(self.databaseinfra,
                                               factory.FakeCredential())

    def test_get_all_instances(self):
        instances = self.dbaas_api.get_all_instances()
        infra_instances = self.databaseinfra.instances.all()
        self.assertListEqual(instances, infra_instances)

    def test_databaseinfra_driver(self):
        driver = self.dbaas_api.get_databaseinfra_driver()
        self.assertIsInstance(driver, factory.Driver)

    def test_get_hosts(self):
        instances = self.databaseinfra.instances.all()
        hosts = list(set([instance.hostname for instance in instances]))
        self.assertEqual(hosts, self.dbaas_api.get_hosts())

    def tearDown(self):
        pass


class TestZabbixApi(unittest.TestCase):
    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        zabbix_api = factory.FakeZabbixAPI
        dbaas_api = DatabaseAsAServiceApi(self.databaseinfra,
                                          factory.FakeCredential())
        self.zabbix_provider = factory.FakeDatabaseZabbixProvider(dbaas_api, zabbix_api)

    def test_create_basic_monitors(self):
        self.zabbix_provider.create_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_create_basic_monitor_call(last_calls)

    def assert_create_basic_monitor_call(self, last_calls):
        method = 'globo.createBasicMonitors'
        hosts = self.zabbix_provider.get_hosts()
        for index, call in enumerate(last_calls):
            params = call.get('params')
            host = hosts[index]

            ip = params.get('ip')
            hostname = params.get('host')
            clientgroup = params.get('clientgroup')
            method_called = call.get('method')

            self.assertEqual(ip, host.address)
            self.assertEqual(hostname, host.hostname)
            self.assertEqual(clientgroup, self.zabbix_provider.clientgroup)
            self.assertEqual(method_called, method)

    def test_delete_monitors(self):
        self.zabbix_provider.delete_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_delete_monitors(last_calls)

    def assert_delete_monitors(self, last_calls):
        method = 'globo.deleteMonitors'
        hosts = self.zabbix_provider.get_hosts()
        for index, call in enumerate(last_calls):
            host = hosts[index]

            hostname = call.get('params')[0]
            method_called = call.get('method')

            self.assertEqual(hostname, host.hostname)
            self.assertEqual(method_called, method)

    def test_delete_database_monitors(self):
        self.zabbix_provider.delete_database_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_delete_database_monitors(last_calls)

    def assert_delete_database_monitors(self, last_calls):
        method = 'globo.deleteMonitors'
        instances = self.zabbix_provider.get_all_instances()
        for index, call in enumerate(last_calls):
            instance = instances[index]

            dns = call.get('params')[0]
            method_called = call.get('method')

            self.assertEqual(dns, instance.dns)
            self.assertEqual(method_called, method)

    def test_create_web_monitors(self):
        instances = self.zabbix_provider.get_all_instances()
        for instance in instances:
            dbinfra_name = self.zabbix_provider.get_databaseifra_name()
            params = {"address": instance.dns,
                      "port": "80", "regexp": "WORKING",
                      "uri": "/health-check/redis-con/", "var": "redis-con",
                      "alarm": "yes", "notes": dbinfra_name,
                      "clientgroup": [1, 2]}

            self.zabbix_provider._create_web_monitors(**params)
        self.asset_create_web_monitors(instances, params)

    def asset_create_web_monitors(self, instances, params):
        method = 'globo.createWebMonitors'
        for index, instance in enumerate(instances):
            last_call = self.zabbix_provider.api.last_call[index]
            last_call_params = last_call['params']
            params['address'] = instance.dns

            self.assertEqual(last_call['method'], method)
            self.assertEqual(params, last_call_params)

    def tearDown(self):
        pass


class TestProviderFactory(unittest.TestCase):
    def setUp(self):
        self.available_providers = provider_factory.get_available_providers()
        self.provider_name = 'fake'
        databaseinfra = factory.set_up_databaseinfra()
        self.credential = factory.FakeCredential()
        self.dbaas_api = DatabaseAsAServiceApi(databaseinfra,
                                               self.credential)
        self.zabbix_api = factory.FakeZabbixAPI

    def test_get_available_providers(self):
        for provider in self.available_providers:
            provider_name = provider.__name__
            provider_class = database_providers.__getattribute__(provider_name)
            self.assertEquals(provider, provider_class)

    def test_provider_factory_get_provider_class_single(self):
        provider_class = database_providers.FakeSingleZabbixProvider
        self.assert_provider_factory_get_provider_class(False,
                                                        provider_class)

    def test_provider_factory_get_provider_class_ha(self):
        provider_class = database_providers.FakeHAZabbixProvider
        self.assert_provider_factory_get_provider_class(True,
                                                        provider_class)

    def assert_provider_factory_get_provider_class(self, is_ha,
                                                   provider_class):
        provider = provider_factory.ProviderFactory.get_provider_class('fake',
                                                                       is_ha)
        self.assertEqual(provider, provider_class)

    def test_provider_factory_single_instance(self):
        databaseinfra = factory.set_up_databaseinfra(is_ha=False)
        provider_class = database_providers.FakeSingleZabbixProvider

        self.assert_provider_factory(databaseinfra, provider_class)

    def assert_provider_factory(self, databaseinfra, provider_class):
        dbaas_api = DatabaseAsAServiceApi(databaseinfra, self.credential)
        provider = provider_factory.ProviderFactory.factory(dbaas_api,
                                                            zabbix_api=self.zabbix_api)

        self.assertIsInstance(provider, provider_class)

    def test_provider_factory_ha(self):
        databaseinfra = factory.set_up_databaseinfra(is_ha=True)
        provider_class = database_providers.FakeHAZabbixProvider

        self.assert_provider_factory(databaseinfra, provider_class)

    def test_factory_for(self):
        databaseinfra = factory.set_up_databaseinfra(is_ha=False)
        provider = factory_for(databaseinfra=databaseinfra,
                               credentials=self.credential,
                               zabbix_api=self.zabbix_api)

        self.assertIsInstance(provider,
                              database_providers.FakeSingleZabbixProvider)

    def test_provider_class_does_not_exists(self):
        databaseinfra = factory.set_up_databaseinfra(is_ha=False,
                                                     name='bazinga')

        def call_factpry():
            factory_for(databaseinfra=databaseinfra,
                        credentials=self.credential,
                        zabbix_api=self.zabbix_api)

        self.assertRaises(NotImplementedError, callableObj=call_factpry)

    def tearDown(self):
        pass
