# -*- coding: utf-8 -*-


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra, credentials):
        self.databaseinfra = databaseinfra
        self.credentials = credentials

    @property
    def user(self):
        return self.credentials.user

    @property
    def password(self):
        return self.credentials.password

    @property
    def endpoint(self):
        return self.credentials.endpoint

    @property
    def main_clientgroup(self):
        return self.credentials.get_parameter_by_name("main_clientgroup")

    @property
    def extra_clientgroup(self):
        return self.credentials.get_parameter_by_name("extra_clientgroup")

    def extra_parameters(self, group):
        return self.credentials.get_parameters_by_group(group)

    @property
    def alarm_notes(self):
        return self.credentials.get_parameter_by_name("alarm_notes")

    @property
    def instances(self):
        return self.databaseinfra.instances.all()

    @property
    def driver(self):
        return self.databaseinfra.get_driver()

    @property
    def database_instances(self):
        return self.driver.get_database_instances()

    @property
    def non_database_instances(self):
        return self.driver.get_non_database_instances()

    @property
    def hosts(self):
        return list({instance.hostname for instance in self.instances})

    @property
    def databaseifra_name(self):
        return self.databaseinfra.name

    @property
    def secondary_ips(self):
        return self.databaseinfra.cs_dbinfra_attributes.all()

    @property
    def is_ha(self):
        return self.databaseinfra.plan.is_ha

    @property
    def engine_name(self):
        return self.databaseinfra.engine.engine_type.name

    @property
    def engine_version(self):
        return self.databaseinfra.engine.version
