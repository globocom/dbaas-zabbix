from dbaas_zabbix.custom_exceptions import NotImplementedError
from dbaas_zabbix import database_providers


class ProviderFactory(object):
    @classmethod
    def get_provider_class(cls, driver_name, is_ha):
        for klass in get_available_providers():
            name_eq_klass = driver_name == klass.__provider_name__
            is_ha_eq_klass = is_ha == klass.__is_ha__

            if name_eq_klass and is_ha_eq_klass:
                return klass

        raise NotImplementedError()

    @classmethod
    def factory(cls, dbaas_api, **kwargs):
        driver_name = dbaas_api.get_databaseinfra_engine_name()
        is_ha = dbaas_api.get_databaseinfra_plan_is_ha()

        driver_class = cls.get_provider_class(driver_name, is_ha)
        return driver_class(dbaas_api=dbaas_api, **kwargs)


def get_available_providers():
    available_objects = dir(database_providers)
    available_objects = filter(lambda klass: 'Provider' in klass,
                               available_objects)

    return [database_providers.__getattribute__(klass)for klass in
            available_objects]
