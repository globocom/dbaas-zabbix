# -*- coding: utf-8 -*-


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra):
        self.databaseinfra = databaseinfra
        self.driver = self.get_databaseinfra_driver()
        self.database_instances = self.get_database_instances()

    def get_all_instances(self, ):
        return self.databaseinfra.instances.all()

    def get_databaseinfra_driver(self):
        return self.databaseinfra.get_driver()

    def get_database_instances(self):
        return self.driver.get_database_instances()

    def get_non_database_instances(self,):
        return self.driver.get_non_database_instances()

    def get_hosts(self,):
        instances = self.get_all_instances()
        return list(set([instance.hostname for instance in instances]))

    def get_environment(self):
        return self.databaseinfra.environment

    def get_databaseifra_name(self):
        return self.databaseinfra.name

    def get_databaseinfra_secondary_ips(self):
        return self.databaseinfra.cs_dbinfra_attributes.all()

    def get_databaseinfra_availability(self):
        return self.databaseinfra.plan.is_ha

    def get_databaseinfra_engine_name(self):
        return self.databaseinfra.engine.engine_type.name
