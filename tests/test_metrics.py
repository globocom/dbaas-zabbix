import unittest
from dbaas_zabbix.metrics import ZabbixMetrics, KEY_DISK_USED_DATA, KEY_DISK_SIZE_DATA
from dbaas_zabbix.errors import ZabbixApiKeyNotFoundError, ZabbixApiNoDataBetweenTimeError
from . import FakeApi, FakeHost

KEYS = [KEY_DISK_SIZE_DATA, KEY_DISK_USED_DATA]


class TestZabbixMetricsApi(unittest.TestCase):
    def setUp(self):
        self.api = FakeApi()
        self.group = 2
        self.host = FakeHost(name='fake_host')
        self.metrics = ZabbixMetrics(zappix_api=self.api, group=self.group)

    def test_can_get_items(self):
        self.api.item.add_disk_data_size_item(
            item_id=123, host=self.host, group=self.group
        )
        self.api.item.add_disk_data_used_item(
            item_id=456, host=self.host, group=self.group
        )

        items = self.metrics.get_items(
            key=KEY_DISK_SIZE_DATA, host_name=self.host.hostname
        )
        self.assertEqual(1, len(items))
        self.assertEqual(2, len(items[0]))
        self.assertIn('itemid', items[0])
        self.assertIn('value_type', items[0])

        items = self.metrics.get_items(
            key=KEY_DISK_USED_DATA, host_name=self.host.hostname
        )
        self.assertEqual(1, len(items))
        self.assertEqual(2, len(items[0]))
        self.assertIn('itemid', items[0])
        self.assertIn('value_type', items[0])

    def test_empty_item_list(self):
        items = self.metrics.get_items(
            key=KEY_DISK_USED_DATA, host_name=self.host.hostname
        )
        self.assertEqual(0, len(items))

    def test_check_item_filters(self):
        self.metrics.get_items(
            key=KEY_DISK_SIZE_DATA, host_name=self.host.hostname
        )

        last_filter = self.api.item.last_filter
        self.assertEqual(5, len(last_filter))
        self.assertIn('key_', last_filter)
        self.assertEqual(last_filter['key_'], KEY_DISK_SIZE_DATA)
        self.assertIn('group', last_filter)
        self.assertEqual(last_filter['group'], self.group)
        self.assertIn('host', last_filter)
        self.assertEqual(last_filter['host'], self.host.hostname)
        self.assertIn('status', last_filter)
        self.assertEqual(last_filter['status'], 0)
        self.assertIn('state', last_filter)
        self.assertEqual(last_filter['state'], 0)

    def test_can_get_history(self):
        self.api.history.add_history(123, 3, 550, 200)
        self.api.history.add_history(123, 3, 600, 210)
        self.api.history.add_history(123, 3, 650, 220)

        self.api.history.add_history(456, 3, 1950, 1200)
        self.api.history.add_history(456, 3, 2200, 1300)

        histories = self.metrics.get_history(3, [123, 456], 217, 1217)
        self.assertEqual(2, len(histories))
        self.assertEqual(3, len(histories[0]))
        self.assertIn('itemid', histories[0])
        self.assertIn('value', histories[0])
        self.assertIn('clock', histories[0])
        self.assertEqual(123, histories[0]['itemid'])
        self.assertEqual(650, histories[0]['value'])
        self.assertEqual(220, histories[0]['clock'])

        self.assertEqual(3, len(histories[1]))
        self.assertIn('itemid', histories[1])
        self.assertIn('value', histories[1])
        self.assertIn('clock', histories[1])
        self.assertEqual(456, histories[1]['itemid'])
        self.assertEqual(1950, histories[1]['value'])
        self.assertEqual(1200, histories[1]['clock'])

    def test_empty_history_list(self):
        histories = self.metrics.get_history(3, [123, 456], 217, 1217)
        self.assertEqual(0, len(histories))

    def test_check_history_request(self):
        history = 3
        items = [123, 456]
        time_from = 217
        time_till = 1217
        self.metrics.get_history(history, items, time_from, time_till)

        request = self.api.history.last_request
        self.assertEqual(5, len(request))
        self.assertIn('output', request)
        self.assertEqual(request['output'], 'extend')
        self.assertIn('history', request)
        self.assertEqual(request['history'], history)
        self.assertIn('itemids', request)
        self.assertEqual(request['itemids'], items)
        self.assertIn('time_from', request)
        self.assertEqual(request['time_from'], time_from)
        self.assertIn('time_till', request)
        self.assertEqual(request['time_till'], time_till)


    def test_can_get_metrics(self):
        self.api.item.add_disk_data_size_item(
            item_id=123, host=self.host, group=self.group
        )
        self.api.item.add_disk_data_used_item(
            item_id=456, host=self.host, group=self.group
        )

        self.api.history.add_history(123, 3, 550, 200)
        self.api.history.add_history(123, 3, 600, 210)
        self.api.history.add_history(123, 3, 650, 220)
        self.api.history.add_history(456, 3, 1950, 1200)
        self.api.history.add_history(456, 3, 2200, 1300)

        metrics = self.metrics.get_metrics(217, 1217, KEYS, self.host)
        self.assertEqual(len(KEYS), len(metrics))

        for key in KEYS:
            self.assertEqual(1, len(metrics[key]))

    def test_cannot_get_metrics_without_items(self):
        self.assertRaises(
            ZabbixApiKeyNotFoundError,
            self.metrics.get_metrics, 217, 1217, KEYS, self.host
        )

    def test_cannot_get_metrics_without_history(self):
        self.api.item.add_disk_data_used_item(
            item_id=456, host=self.host, group=self.group
        )
        self.api.item.add_disk_data_size_item(
            item_id=456, host=self.host, group=self.group
        )
        self.assertRaises(
            ZabbixApiNoDataBetweenTimeError,
            self.metrics.get_metrics, 217, 1217, KEYS, self.host
        )

