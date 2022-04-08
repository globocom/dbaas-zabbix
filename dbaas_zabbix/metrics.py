from collections import OrderedDict
from dbaas_zabbix.errors import ZabbixApiKeyNotFoundError, ZabbixApiNoDataBetweenTimeError

KEY_DISK_SIZE_DATA = 'hrStorageSizeInBytes[/data]'
KEY_DISK_USED_DATA = 'hrStorageUsedInBytes[/data]'


class ZabbixMetrics(object):

    def __init__(self, zappix_api, group):
        self.api = zappix_api
        self.group = group

    def get_items(self, key, hostname):
        return self.api.item.get(
                output=['itemid', 'value_type'],
                search={'key_': key},
                group=self.group,
                filter={'host': hostname, 'status': 0, 'state': 0}
            )

    def get_history(self, value_type, items, time_from, time_till):
        return self.api.history.get(
            output='extend',
            history=value_type,
            itemids=items,
            time_from=time_from,
            time_till=time_till
        )

    def get_metrics(self, time_from, time_till, keys, hostname):
        items = {}
        value_type = 0

        for key in keys:
            item = self.get_items(key, hostname)
            if not item:
                raise ZabbixApiKeyNotFoundError(host=hostname, key=key)

            value_type = item[0]['value_type']
            items[item[0]['itemid']] = key

        metrics = {}
        histories = self.get_history(
            value_type=value_type, items=items.keys(),
            time_from=time_from, time_till=time_till
        )

        if not histories:
            raise ZabbixApiNoDataBetweenTimeError(
                host=hostname, keys=keys,
                time_from=time_from, time_till=time_till
            )

        for history in histories:
            key = items[history['itemid']]
            if key not in metrics:
                metrics[key] = OrderedDict()
            metrics[key][history['clock']] = history['value']

        return metrics

    def get_last_value(self, key, hostname):
        from time import localtime, mktime
        current_time = int(mktime(localtime()))

        metrics = self.get_metrics(
            time_from=current_time-3600,
            time_till=current_time,
            keys=[key],
            hostname=hostname
        )[key]
        last_key = metrics.keys()[-1]
        return metrics[last_key]

    def get_current_disk_data_size(self, hostname):
        current_value = self.get_last_value(key=KEY_DISK_SIZE_DATA, hostname=hostname)
        return int(current_value) / 1024

    def get_current_disk_data_used(self, hostname):
        current_value = self.get_last_value(key=KEY_DISK_USED_DATA, hostname=hostname)
        return int(current_value) / 1024
