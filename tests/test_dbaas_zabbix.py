#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from dbaas_zabbix import provider
from tests import factory


class TestDatabaseAsAServiceApi(unittest.TestCase):

    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        self.dbaas_api = provider.DatabaseAsAServiceApi(self.databaseinfra)

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
        self.zabbix_provider = provider.ZabbixProvider('fake_user',
                                                       'fake_pas@123',
                                                       'fake.endpoint.com',
                                                       [1, 2],
                                                       self.databaseinfra,
                                                       factory.FakeZabbixAPI)

    def test_create_basic_monitors(self):
        self.zabbix_provider._create_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_create_basic_monitor_call(last_calls)

    def assert_create_basic_monitor_call(self, last_calls):
        method = 'globo.createBasicMonitors'
        hosts = self.zabbix_provider.get_hosts()
        for index, call in enumerate(last_calls):
            params = call.get('params')[0]
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
        self.zabbix_provider._delete_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_delete_monitors(last_calls)

    def assert_delete_monitors(self, last_calls):
        method = 'globo.deleteMonitors'
        hosts = self.zabbix_provider.get_hosts()
        for index, call in enumerate(last_calls):
            params = call.get('params')[0]
            host = hosts[index]

            hostname = params.get('host')
            method_called = call.get('method')

            self.assertEqual(hostname, host.hostname)
            self.assertEqual(method_called, method)

    def test_delete_database_monitors(self):
        self.zabbix_provider._delete_database_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_delete_database_monitors(last_calls)

    def assert_delete_database_monitors(self, last_calls):
        method = 'globo.deleteMonitors'
        instances = self.zabbix_provider.get_all_instances()
        for index, call in enumerate(last_calls):
            params = call.get('params')[0]
            instance = instances[index]

            dns = params.get('host')
            method_called = call.get('method')

            self.assertEqual(dns, instance.dns)
            self.assertEqual(method_called, method)

    def tearDown(self):
        pass
