#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Old Keys
# KEY_DISK_SIZE_DATA = 'hrStorageSizeInBytes[/data]'
# KEY_DISK_USED_DATA = 'hrStorageUsedInBytes[/data]'

# New Keys
# Values in Bytes
KEY_DISK_SIZE_DATA = 'vfs.fs.size[/data,total]'
KEY_DISK_USED_DATA = 'vfs.fs.size[/data,used]'


class Item(object):

    def __init__(self):
        self.items = []
        self.last_filter = {}

    def get(self, output, filter, search, group):
        filters = {}
        filters.update(filter)
        filters.update(search)
        filters.update({'group': group})
        self.last_filter = filters

        founds = []
        for item in self.items:
            for key, value in filters.items():
                if item[key] != value:
                    break
            else:
                fields = {}
                for output in output:
                    fields.update({output: item[output]})
                founds.append(fields)
        return founds

    def add_item(
            self, item_id, key, host, group, value_type=3, status=0, state=0
    ):
        self.items.append({
            'itemid': item_id,
            'value_type': value_type,
            'key_': key,
            'host': host,
            'group': group,
            'status': status,
            'state': state
        })

    def add_disk_data_used_item(self, item_id, host, group):
        self.add_item(
            item_id=item_id, key=KEY_DISK_USED_DATA,
            host=host.hostname, group=group
        )

    def add_disk_data_size_item(self, item_id, host, group):
        self.add_item(
            item_id=item_id, key=KEY_DISK_SIZE_DATA,
            host=host.hostname, group=group
        )


class History(object):

    def __init__(self):
        self.histories = []
        self.last_request = {}

    def get(self, output, history, itemids, time_from, time_till):
        self.last_request = {
            'output': output, 'history': history, 'itemids': itemids,
            'time_from': time_from, 'time_till': time_till
        }

        founds = []
        for history in self.histories:
            is_between_time = (history['time'] > time_from and history['time'] < time_till)
            if not is_between_time:
                continue

            for item_id in itemids:
                if item_id != history['item_id']:
                    founds.append({
                        'itemid': history['item_id'],
                        'clock': history['time'],
                        'value': history['value']
                    })
        return founds

    def add_history(self, item_id, history, value, time):
        self.histories.append({
            'item_id': item_id,
            'history': history,
            'value': value,
            'time': time,
        })


class FakeApi(object):

    def __init__(self):
        self.item = Item()
        self.history = History()


class FakeHost(object):

    def __init__(self, name):
        self.hostname = name
