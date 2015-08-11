#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from dbaas_zabbix import provider
from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from tests import factory


class TestDatabaseAsAServiceApi(unittest.TestCase):

    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        self.dbaas_api = DatabaseAsAServiceApi(self.databaseinfra)

    def test_get_all_instances(self):
        instances = self.dbaas_api.get_all_instances()
        infra_instances = self.databaseinfra.instances.all()
        self.assertEqual(instances, infra_instances)

    def test_databaseinfra_driver(self):
        driver = self.dbaas_api.get_databaseinfra_driver()
        self.assertIsInstance(driver, factory.Driver)

    def test_get_hosts(self):
        instances = self.databaseinfra.instances.all()
        hosts = [instance.hostname for instance in instances]
        self.assertEqual(hosts, self.dbaas_api.get_hosts())

    def tearDown(self):
        pass


class TestZabbixApi(unittest.TestCase):

    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        api_class = factory.FakeZabbixAPI
        self.zabbix_provider = factory.FakeZabbixProvider('fake_user',
                                                          'fake_pas@123',
                                                          'fake.endpoint.com',
                                                          [1, 2],
                                                          self.databaseinfra,
                                                          api_class)

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
            self.assertEqual(clientgroup, self.zabbix_provider.clientgroups)
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
        instances = self.zabbix_provider.get_all_instances()
        self.zabbix_provider._delete_database_monitors(instances)
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
        dbinfra_name = self.zabbix_provider.get_databaseifra_name()
        params = {"port": "80", "regexp": "WORKING",
                  "uri": "/health-check/redis-con/", "var": "redis-con",
                  "alarm": "yes", "notes": dbinfra_name,
                  "clientgroup": [1, 2]}

        self.zabbix_provider._create_web_monitors(instances, **params)
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
