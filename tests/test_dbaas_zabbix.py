#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from dbaas_zabbix.dbaas_api import DatabaseAsAServiceApi
from dbaas_zabbix import provider
from dbaas_zabbix import provider_factory
from dbaas_zabbix import database_providers
from dbaas_zabbix import factory_for
from tests import factory


class TestDatabaseAsAServiceApi(unittest.TestCase):
    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        self.dbaas_api = DatabaseAsAServiceApi(self.databaseinfra,
                                               factory.FakeCredential())

    def test_get_all_instances(self):
        instances = self.dbaas_api.instances
        infra_instances = self.databaseinfra.instances.all()
        self.assertListEqual(instances, infra_instances)

    def test_databaseinfra_driver(self):
        driver = self.dbaas_api.driver
        self.assertIsInstance(driver, factory.Driver)

    def test_get_hosts(self):
        instances = self.databaseinfra.instances.all()
        hosts = list(set([instance.hostname for instance in instances]))
        self.assertEqual(hosts, self.dbaas_api.hosts)

    def tearDown(self):
        pass


class TestZabbixApi(unittest.TestCase):

    @property
    def credential(self):
        return factory.FakeCredential()

    def setUp(self):
        self.databaseinfra = factory.set_up_databaseinfra()
        self.zabbix_api = factory.FakeZabbixAPI
        self.dbaas_api = DatabaseAsAServiceApi(
            self.databaseinfra, self.credential
        )
        self.zabbix_provider = factory.FakeDatabaseZabbixProvider(
            self.dbaas_api, self.zabbix_api
        )

    def test_create_basic_monitors(self):
        self.zabbix_provider.create_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_create_basic_monitor_call(last_calls)

    def assert_create_basic_monitor_call(self, last_calls):
        method = 'globo.createLinuxMonitors'
        hosts = self.zabbix_provider.hosts
        for index, call in enumerate(last_calls):
            params = call.get('params')
            host = hosts[index]

            ip = params.get('ip')
            hostname = params.get('host')
            hostgroups = params.get('hostgroups')
            provider_hostgroups = self.zabbix_provider.dbaas_api.client_group_host
            method_called = call.get('method')

            self.assertEqual(ip, host.address)
            self.assertEqual(hostname, host.hostname)
            self.assertEquals(hostgroups, provider_hostgroups)
            self.assertEqual(method_called, method)
            self.assertNotIn("notification_slack", params)

    def test_delete_monitors(self):
        self.zabbix_provider.delete_basic_monitors()
        last_calls = self.zabbix_provider.api.last_call
        self.assert_delete_monitors(last_calls)

    def assert_delete_monitors(self, last_calls):
        method = 'globo.deleteMonitors'
        hosts = self.zabbix_provider.hosts
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
        instances = self.zabbix_provider.instances
        for index, call in enumerate(last_calls):
            instance = instances[index]

            dns = call.get('params')[0]
            method_called = call.get('method')

            self.assertEqual(dns, instance.dns)
            self.assertEqual(method_called, method)

    def test_create_web_monitors(self):
        instances = self.zabbix_provider.instances
        for instance in instances:
            dbinfra_name = self.zabbix_provider.databaseifra_name
            params = {"address": instance.dns,
                      "port": "80", "regexp": "WORKING",
                      "uri": "/health-check/redis-con/", "var": "redis-con",
                      "alarm": "yes", "notes": dbinfra_name,
                      "hostgroups": self.dbaas_api.client_group_database}

            self.zabbix_provider._create_web_monitors(**params)
        self.asset_create_web_monitors(instances, params)

    def asset_create_web_monitors(self, instances, params):
        method = 'globo.createWebMonitors'
        for index, instance in enumerate(instances):
            last_call = self.zabbix_provider.api.last_call[index]
            last_call_params = last_call['params']

            self.assert_slack(last_call_params)
            last_call_params.pop("notification_slack", None)

            params['address'] = instance.dns

            self.assertEqual(last_call['method'], method)
            self.assertEqual(params, last_call_params)

    def test_get_disable_alarms(self):
        host = {"host": "test"}
        self.zabbix_provider._disable_alarms(host=host)

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["host"], host)
        self.assertEquals(last_call["method"], "globo.disableAlarms")

    def test_get_enable_alarms(self):
        host = {"host": "test"}
        self.zabbix_provider._enable_alarms(host=host)

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["host"], host)
        self.assertEquals(last_call["method"], "globo.enableAlarms")

    def test_get_host_info(self):
        host_filter = {"host": "test"}
        self.zabbix_provider._get_host_info(output="extend",
                                            filter=host_filter)

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["output"], "extend")
        self.assertEquals(last_call_params["filter"], host_filter)
        self.assertEquals(last_call["method"], "host.get")

    def test_get_host_group_info(self):
        host_group_filter = {"name": "test"}
        self.zabbix_provider._get_host_group_info(output="extend",
                                                  filter=host_group_filter)

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["output"], "extend")
        self.assertEquals(last_call_params["filter"], host_group_filter)
        self.assertEquals(last_call["method"], "hostgroup.get")

    def test_update_host_info(self):
        self.zabbix_provider._update_host_info(hostid="2132",
                                               groups=[1, 2, 3])

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEqual(last_call_params["hostid"], "2132")
        self.assertEqual(last_call["method"], "host.update")

    def test_create_mysql_monitors(self):
        self.zabbix_provider._create_mysql_monitors(
            alarm='group', host='fake01.test.com')

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["alarm"], 'group')
        self.assertEquals(last_call_params["host"], 'fake01.test.com')
        self.assertEquals(last_call["method"], "globo.createMySQLMonitors")
        self.assert_slack(last_call_params)

    def test_create_mongo_monitors(self):
        self.zabbix_provider._create_mongo_monitors(
            alarm='group', host='fake02.test.com'
        )

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["alarm"], 'group')
        self.assertEquals(last_call_params["host"], 'fake02.test.com')
        self.assertEquals(last_call["method"], "globo.createMongoMonitors")
        self.assert_slack(last_call_params)

    def test_update_host_interface(self):
        self.zabbix_provider._update_host_interface(hostid="2133")

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEqual(last_call_params["hostid"], "2133")
        self.assertEqual(last_call["method"], "hostinterface.update")

    def test_get_host_interface(self):
        self.zabbix_provider._get_host_interface(hostid="2134")

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call["method"], "hostinterface.get")
        self.assertEqual(last_call_params["hostid"], "2134")

    def test_get_host_id(self):
        host_id = self.zabbix_provider.get_host_id(
            host_name="fake"
        )

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call["method"], "host.get")
        self.assertEquals(
            last_call_params["search"]["name"], "fake"
        )
        self.assertEqual(host_id, "3309")

    def test_get_triggers(self):
        my_triggers = {'status': '1', 'triggerid': '1234'}
        self.zabbix_provider.api.add_trigger(
            my_triggers['status'], my_triggers['triggerid']
        )

        triggers = self.zabbix_provider.get_host_triggers(host_name="fake")

        last_call = self.zabbix_provider.api.last_call[1]
        self.assertEquals(last_call["method"], "trigger.get")

        self.assertIsNotNone(triggers)
        self.assertIsInstance(triggers, list)
        self.assertEqual(len(triggers), 1)
        self.assertIn('status', triggers[0])
        self.assertIn('triggerid', triggers[0])
        self.assertEqual(my_triggers['status'], triggers[0]['status'])
        self.assertEqual(my_triggers['triggerid'], triggers[0]['triggerid'])

    def test_get_triggers_empty(self):
        triggers = self.zabbix_provider.get_host_triggers(host_name="fake")

        last_call = self.zabbix_provider.api.last_call[1]
        self.assertEquals(last_call["method"], "trigger.get")
        self.assertIsInstance(triggers, list)
        self.assertEqual(triggers, [])

    def test_trigger_status(self):
        self.assertEqual(provider.STATUS_ENABLE, 0)
        self.assertEqual(provider.STATUS_DISABLE, 1)

    def test_all_alarms_enabled(self):
        self.zabbix_provider.api.add_trigger(provider.STATUS_ENABLE, 123)
        self.zabbix_provider.api.add_trigger(provider.STATUS_ENABLE, 456)
        self.zabbix_provider.api.add_trigger(provider.STATUS_ENABLE, 789)
        self.assertTrue(self.zabbix_provider.is_alarms_enabled())

    def test_all_alarms_disabled(self):
        self.zabbix_provider.api.add_trigger(provider.STATUS_DISABLE, 123)
        self.zabbix_provider.api.add_trigger(provider.STATUS_DISABLE, 456)
        self.zabbix_provider.api.add_trigger(provider.STATUS_DISABLE, 789)
        self.assertFalse(self.zabbix_provider.is_alarms_enabled())

    def test_some_alarms_disabled(self):
        self.zabbix_provider.api.add_trigger(provider.STATUS_ENABLE, 123)
        self.zabbix_provider.api.add_trigger(provider.STATUS_DISABLE, 456)
        self.zabbix_provider.api.add_trigger(provider.STATUS_ENABLE, 789)
        self.assertFalse(self.zabbix_provider.is_alarms_enabled())

    def test_can_not_get_host_id(self):
        host_id = self.zabbix_provider.get_host_id(
            host_name="fake.wrong"
        )
        self.assertIsNone(host_id)

    def test_get_host_interface_id(self):
        host_id = self.zabbix_provider.get_host_interface_id(
            host_id="9981"
        )

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call["method"], "hostinterface.get")
        self.assertEquals(last_call_params["hostids"], "9981")
        self.assertEqual(host_id, "3310")

    def test_not_implemented_methods_throws_exceptions(self):
        from dbaas_zabbix.provider import ZabbixProvider
        zabbix_provider = ZabbixProvider(self.dbaas_api, self.zabbix_api)

        with self.assertRaises(NotImplementedError):
            zabbix_provider.create_database_monitors()

        with self.assertRaises(NotImplementedError):
            zabbix_provider.delete_database_monitors()

        with self.assertRaises(NotImplementedError):
            zabbix_provider.create_basic_monitors()

        with self.assertRaises(NotImplementedError):
            zabbix_provider.delete_basic_monitors()

        with self.assertRaises(NotImplementedError):
            zabbix_provider.update_host_interface(host_name='test')

    def test_create_tcp_monitors(self):
        self.zabbix_provider._create_tcp_monitors(
            doc='Get in touch with me', port=9003, host='fake07.test.com')

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["port"], 9003)
        self.assertEquals(last_call_params["host"], 'fake07.test.com')
        self.assertEquals(last_call["method"], "globo.createTCPMonitors")
        self.assert_slack(last_call_params)

    def test_create_redis_monitors(self):
        self.zabbix_provider._create_redis_monitors(
            host='fake08.redis.com', password="StrongPWD123",
            port=6379, alarm='yes', notes='Get in touch with me',
        )

        last_call = self.zabbix_provider.api.last_call[0]
        last_call_params = last_call['params']
        self.assertEquals(last_call_params["port"], 6379)
        self.assertEquals(last_call_params["host"], 'fake08.redis.com')
        self.assertEquals(last_call["method"], "globo.createRedisMonitors")
        self.assert_slack(last_call_params)

    def assert_slack(self, params_call):
        slack = self.zabbix_provider.dbaas_api.slack_notification
        if not slack:
            self.assertNotIn("notification_slack", params_call)
        else:
            self.assertIn("notification_slack", params_call)
            self.assertEqual(params_call["notification_slack"], slack)

    def tearDown(self):
        pass


class TestProviderFactory(unittest.TestCase):
    def setUp(self):
        self.available_providers = provider_factory.available_providers()
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
                                                        provider_class,
                                                        '0.0.0')

    def test_provider_factory_get_provider_class_ha(self):
        provider_class = database_providers.FakeHAZabbixProvider
        self.assert_provider_factory_get_provider_class(True,
                                                        provider_class,
                                                        '1.1.1')

    def assert_provider_factory_get_provider_class(self, is_ha,
                                                   provider_class,
                                                   version):
        provider = provider_factory.ProviderFactory.get_provider_class('fake',
                                                                       is_ha,
                                                                       version)
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
        databaseinfra.engine.version = '1.1.1'

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

        def call_factory():
            factory_for(databaseinfra=databaseinfra,
                        credentials=self.credential,
                        zabbix_api=self.zabbix_api)

        self.assertRaises(NotImplementedError, callableObj=call_factory)

    def test_get_all_hosts_name(self):
        databaseinfra = factory.set_up_databaseinfra(is_ha=False)
        provider = factory_for(
            databaseinfra=databaseinfra,
            credentials=self.credential,
            zabbix_api=self.zabbix_api
        )
        infra_hosts = (
            [host.hostname for host in provider.hosts] +
            provider.get_zabbix_databases_hosts()
        )
        provider_hosts = provider.get_all_hosts_name()
        self.assertEqual(len(infra_hosts), len(provider_hosts))

    def tearDown(self):
        pass


class TestProviderFactorySlack(TestZabbixApi):

    @property
    def credential(self):
        return factory.FakeCredentialWithSlack()
