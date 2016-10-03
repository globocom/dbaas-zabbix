class ZabbixMetricsError(EnvironmentError):
    pass


class ZabbixApiKeyNotFoundError(ZabbixMetricsError):
    def __init__(self, host, key):
        msg = 'Host "{}" don\'t have "{}"'.format(host, key)
        super(ZabbixMetricsError, self).__init__(msg)


class ZabbixApiNoDataBetweenTimeError(ZabbixMetricsError):
    def __init__(self, host, keys, time_from, time_till):
        msg = 'Host "{}" don\'t have "{}" between {} and {}'.format(
            host, keys, time_from, time_till
        )
        super(ZabbixMetricsError, self).__init__(msg)




