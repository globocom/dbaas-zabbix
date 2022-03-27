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
    def client_group_host(self):
        return list(self.extra_parameters("group_host").values())

    @property
    def client_group_database(self):
        return list(self.extra_parameters("group_database").values())

    def extra_parameters(self, group):
        return self.credentials.get_parameters_by_group(group)

    @property
    def main_clientgroup(self):
        return self.credentials.get_parameter_by_name("main_clientgroup")

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
        if self.using_agent:
            return []
        return list({instance.hostname for instance in self.instances})

    @property
    def databaseifra_name(self):
        return self.databaseinfra.name

    @property
    def mysql_infra_dns_from_endpoint_dns(self):
        return self.databaseinfra.endpoint_dns.split(':')[0]

    @property
    def is_ha(self):
        return self.databaseinfra.plan.is_ha

    @property
    def engine_name(self):
        return self.databaseinfra.engine.engine_type.name

    @property
    def engine_version(self):
        return self.databaseinfra.engine_patch.full_version

    @property
    def slack_notification(self):
        return self.credentials.get_parameter_by_name("slack_notification")

    @property
    def database(self):
        return self.databaseinfra.databases.first()

    @property
    def organization_hostgroup(self):
        organization = self.database.team.organization
        if organization:
            return organization.get_grafana_hostgroup_external_org()
        return None

    @property
    def using_agent(self):
        zabbix_agent = self.credentials.get_parameter_by_name("zabbix_agent")
        if zabbix_agent.lower() == 'true':
            return True
        return False
