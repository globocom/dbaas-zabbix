# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)
STATUS_ENABLE = 0
STATUS_DISABLE = 1


def set_client_group(attribute):
    def decorator(method):
        def wrapper(*args, **kwargs):
            self = args[0]
            kwargs["hostgroups"] = list(getattr(self.dbaas_api, attribute))
            org_hostgroup = self.dbaas_api.organization_hostgroup
            if org_hostgroup:
                kwargs["hostgroups"] += [org_hostgroup,]
            return method(*args, **kwargs)

        return wrapper

    return decorator


def set_slack_notification():
    def decorator(method):
        def wrapper(*args, **kwargs):
            self = args[0]
            notification_to = self.dbaas_api.slack_notification
            if notification_to:
                kwargs["notification_slack"] = notification_to
            return method(*args, **kwargs)

        return wrapper

    return decorator


class ZabbixProvider(object):
    __provider_name__ = None
    __is_ha__ = None
    __version__ = []

    def __init__(self, dbaas_api, zabbix_api):
        self.dbaas_api = dbaas_api
        self.api = zabbix_api(dbaas_api.endpoint)
        self.api.session.verify=False
        self.api.login(user=dbaas_api.user, password=dbaas_api.password)

    @property
    def zabbix_version(self):
        version = self.dbaas_api.engine_version.split('.')
        return "{}.{}".format(version[0], version[1])

    def logout(self):
        try:
            self.api.user.logout()
        except Exception as e:
            LOG.error('Could not logout. Error: {}'.format(e))

    def __getattr__(self, name):
        return getattr(self.dbaas_api, name)

    def _delete_monitors(self, host):
        LOG.info("Destroying monitor for host: {}".format(host))
        return self.api.globo.deleteMonitors(host)

    @set_client_group("client_group_host")
    def _create_basic_monitors(self, **kwargs):
        LOG.info("Creating basic monitor with params: {}".format(kwargs))
        return self.api.globo.createLinuxMonitors(**kwargs)

    @set_client_group("client_group_database")
    @set_slack_notification()
    def _create_web_monitors(self, **kwargs):
        LOG.info("Creating web monitor with params: {}".format(kwargs))
        return self.api.globo.createWebMonitors(**kwargs)

    @set_client_group("client_group_database")
    @set_slack_notification()
    def _create_tcp_monitors(self, **kwargs):
        return self.api.globo.createTCPMonitors(**kwargs)

    @set_client_group("client_group_database")
    @set_slack_notification()
    def _create_redis_monitors(self, **kwargs):
        return self.api.globo.createRedisMonitors(**kwargs)

    @set_client_group("client_group_database")
    @set_slack_notification()
    def _create_mongo_monitors(self, **kwargs):
        return self.api.globo.createMongoMonitors(**kwargs)

    @set_client_group("client_group_database")
    @set_slack_notification()
    def _create_mysql_monitors(self, **kwargs):
        return self.api.globo.createMySQLMonitors(**kwargs)


    def _get_host_info(self, **kwargs):
        return self.api.host.get(**kwargs)

    def _update_host_interface(self, **kwargs):
        return self.api.hostinterface.update(**kwargs)

    def _get_host_interface(self, **kwargs):
        return self.api.hostinterface.get(**kwargs)

    def _update_host_info(self, **kwargs):
        return self.api.host.update(**kwargs)

    def _get_host_group_info(self, **kwargs):
        return self.api.hostgroup.get(**kwargs)

    def _disable_alarms(self, **kwargs):
        return self.api.globo.disableAlarms(**kwargs)

    def _enable_alarms(self, **kwargs):
        return self.api.globo.enableAlarms(**kwargs)

    def get_host_id(self, host_name):
        host_info = self._get_host_info(search={'name': host_name})
        for host in host_info:
            if host['name'] == host_name:
                return host['hostid']
        return None

    def get_host_interface_id(self, host_id):
        host_interface = self.api.hostinterface.get(hostids=host_id)
        return host_interface[0]['interfaceid']

    def create_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_basic_monitors(self, **kwargs):
        raise NotImplementedError

    def create_database_monitors(self, **kwargs):
        raise NotImplementedError

    def delete_database_monitors(self, **kwargs):
        raise NotImplementedError

    def update_host_interface(self, **kwargs):
        raise NotImplementedError

    def get_all_hosts_name(self):
        hosts = []
        for zabbix_host in self.get_zabbix_databases_hosts():
            hosts.append(zabbix_host)

        for host in self.hosts:
            hosts.append(host.hostname)
        return hosts

    def get_host_triggers(self, host_name):
        host_id = self.get_host_id(host_name)
        triggers = self.api.trigger.get(
            output=['status'], hostids=[host_id]
        )

        if not triggers:
            LOG.warning('Host {} does not have triggers'.format(host_name))
        return triggers

    def is_alarms_enabled(self):
        for host in self.get_all_hosts_name():
            for trigger in self.get_host_triggers(host):
                status = int(trigger['status'])
                if status == STATUS_DISABLE:
                    LOG.info(
                        'Trigger {} is disabled for host {}'.format(
                            trigger['triggerid'], host
                        )
                    )
                    return False

        return True

    def get_hostgroup_id(self, hostgroup_name):
        hostgroups = self.api.hostgroup.get(
            search={'name': hostgroup_name})

        for hostgroup in hostgroups:
            if hostgroup['name'] == hostgroup_name:
                return hostgroup['groupid']
        return None

    def add_hostgroup_on_host(self, host_name, hostgroup_name):

        host_id = self.get_host_id(host_name=host_name)
        if not host_id:
            LOG.info('Host id not found for host: {}'.format(host_name))
            return

        hostgroup_id = self.get_hostgroup_id(hostgroup_name=hostgroup_name)
        if not hostgroup_id:
            LOG.info('Hostgroup id not found for hostgroup: {}'.format(
                hostgroup_name))
            return

        self.api.hostgroup.massadd(
            groups={'groupid': hostgroup_id},
            hosts=[host_id,]
        )

    def remove_hostgroup_on_host(self, host_name, hostgroup_name):

        host_id = self.get_host_id(host_name=host_name)
        if not host_id:
            LOG.info('Host id not found for host: {}'.format(host_name))
            return

        hostgroup_id = self.get_hostgroup_id(hostgroup_name=hostgroup_name)
        if not hostgroup_id:
            LOG.info('Hostgroup id not found for hostgroup: {}'.format(
                hostgroup_name))
            return

        self.api.hostgroup.massremove(
            groupids=[hostgroup_id],
            hostids=[host_id]
        )

    def update_macro(self, host_name, macro, value):
        self.api.globo.updateMacro(
            host_name=host_name,
            macro=macro,
            value=value
        )

