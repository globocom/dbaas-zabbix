from dbaas_zabbix import database_providers


class ProviderFactory(object):
    @classmethod
    def get_provider_class(cls, driver_name, is_ha,):
        for klass in available_providers():
            name_eq_klass = driver_name == klass.__provider_name__
            is_ha_eq_klass = is_ha == klass.__is_ha__

            if name_eq_klass and is_ha_eq_klass:
                return klass

        raise NotImplementedError

    @classmethod
    def factory(cls, dbaas_api, **kwargs):
        engine_name = dbaas_api.engine_name
        is_ha = dbaas_api.is_ha
        if kwargs.get('engine_name'):
            engine_name = kwargs.get('engine_name')
            del kwargs['engine_name']
        if kwargs.get('is_ha'):
            is_ha = kwargs.get('is_ha')
            del kwargs['is_ha']
        driver_class = cls.get_provider_class(engine_name, is_ha)
        return driver_class(dbaas_api=dbaas_api, **kwargs)


def available_providers():
    available_objects = dir(database_providers)
    available_klasses = (
        klass for klass in available_objects if 'Provider' in klass
    )

    return (database_providers.__getattribute__(klass)for klass in
            available_klasses)
