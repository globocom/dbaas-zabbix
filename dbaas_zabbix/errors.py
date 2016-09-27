class ZabbixApiError(EnvironmentError):
    pass


class ZabbixApiKeyNotFoundError(ZabbixApiError):
    def __init__(self, host, key):
        msg = 'Host "{}" don\'t have "{}"'.format(host, key)
        super(ZabbixApiError, self).__init__(msg)


class ZabbixApiNoDataBetweenTimeError(ZabbixApiError):
    def __init__(self, host, keys, time_from, time_till):
        msg = 'Host "{}" don\'t have "{}" between {} and {}'.format(
            host, keys, time_from, time_till
        )
        super(ZabbixApiError, self).__init__(msg)




