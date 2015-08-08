class GenericZabbixProviderException(Exception):
    def __init__(self, message=None):
        self.message = "{}: {}".format(type(self).__name__, self.message)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class ZabbixProviderCreateException(GenericZabbixProviderException):
    pass


class ZabbixProviderDeleteException(GenericZabbixProviderException):
    pass


class NotImplementedError(Exception):
    pass
