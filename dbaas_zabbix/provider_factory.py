from dbaas_zabbix import database_providers


class ProviderFactory(object):
    @classmethod
    def get_provider_class(cls, driver_name, is_ha, version):
        for klass in available_providers():
            name_eq_klass = driver_name == klass.__provider_name__
            is_ha_eq_klass = is_ha == klass.__is_ha__
            version_eq_klass = version in klass.__version__

            if name_eq_klass and is_ha_eq_klass and version_eq_klass:
                return klass

        raise NotImplementedError

    @classmethod
    def factory(cls, dbaas_api, **kwargs):
        driver_class = cls.get_provider_class(dbaas_api.engine_name,
                                              dbaas_api.is_ha,
                                              dbaas_api.engine_version)
        return driver_class(dbaas_api=dbaas_api, **kwargs)


def available_providers():
    available_objects = dir(database_providers)
    available_klasses = (
        klass for klass in available_objects if 'Provider' in klass
    )

    return (database_providers.__getattribute__(klass)for klass in
            available_klasses)
