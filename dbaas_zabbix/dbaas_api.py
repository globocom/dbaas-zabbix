# -*- coding: utf-8 -*-


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra, credentialtype):
        self.databaseinfra = databaseinfra
        self.credentialtype = credentialtype
        self.driver = self.get_databaseinfra_driver()
        self.credentials = self.get_credentials()

    def get_credentials(self):
        from dbaas_credentials.credential import Credential
        return Credential.get_credentials(environment=self.get_environment(),
                                          integration=self.credentialtype)

    def get_credential_user(self):
        return self.credentials.user

    def get_credential_password(self):
        return self.credentials.password

    def get_credential_endpoint(self):
        return self.credentials.endpoint

    def get_credential_clientgroup(self):
        return self.credentials.get_parameter_by_name("clientgroup")

    def get_all_instances(self):
        return self.databaseinfra.instances.all()

    def get_databaseinfra_driver(self):
        return self.databaseinfra.get_driver()

    def get_database_instances(self):
        return self.driver.get_database_instances()

    def get_non_database_instances(self):
        return self.driver.get_non_database_instances()

    def get_hosts(self):
        instances = self.get_all_instances()
        return list(set([instance.hostname for instance in instances]))

    def get_environment(self):
        return self.databaseinfra.environment

    def get_databaseifra_name(self):
        return self.databaseinfra.name

    def get_databaseinfra_secondary_ips(self):
        return self.databaseinfra.cs_dbinfra_attributes.all()

    def get_databaseinfra_plan_is_ha(self):
        return self.databaseinfra.plan.is_ha

    def get_databaseinfra_engine_name(self):
        return self.databaseinfra.engine.engine_type.name
