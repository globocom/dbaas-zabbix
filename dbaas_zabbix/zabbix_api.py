# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logging.basicConfig(
                                    level=logging.DEBUG,
                                    format='%(asctime)s %(levelname)s %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                )


class Zabbix(object):

    available_methods = (   'globo_createBasicMonitors',
                                         'globo_deleteMonitors',
                                         'globo_generateGraphs',
                                         'globo_createDBMonitors',
                                         'globo_createWebMonitors',
                                         )

    def __init__(self, url, user, password):

        self.headers = {'content-type': 'application/json'}
        self.user = user
        self.password = password

        api_path = '/api_jsonrpc.php'

        if api_path not in url:
            self.url = url + api_path
        else:
            self.url =  url

        self.token = self.login(self.user, self.password)

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            logging.info("A missing method was called.")
            logging.debug("The method was %r. " % (name))
            logging.debug("It was called with %r and %r as arguments" % (args, kwargs))

            if name not in self.available_methods:
                logging.exception("Method not found")
                return

            method = name
            method = method.replace('_','.')
            logging.info("Method: {}".format(method))

            try:
                params = kwargs['params']
            except KeyError:
                logging.exception('You must provide params.')
                return


            response = self.__make_request__(method= method, params= params)
            return response

        return _missing

    def __make_request__(self, method, params):
        payload = {
                            "method": method,
                            "params": params,
                            "auth": self.token,
                            "jsonrpc": "2.0",
                            "id": random.randrange(0, 1000000)
                         }

        data = json.dumps(payload)
        response = requests.post(self.url,data=data,headers=self.headers)

        try:
            response = response.json()
        except ValueError:
            logging.exception('Could not retrieve a json document')
            return

        try:
            return response['result']
        except KeyError:
            logging.exception('Zabbix Error: {}'.format(response['error']))
            return

    def login(self, user, password):
        method = 'user.login'

        payload = {
                            "method": method,
                            "params": {'user':user, 'password':password},
                            "jsonrpc": "2.0",
                            "id": random.randrange(0, 1000000)
                        }

        data = json.dumps(payload)

        response = requests.post(self.url, data=data,headers=self.headers)

        try:
            response = response.json()
        except ValueError:
            logging.exception('Could not retrieve a json document')
            return

        try:
            return response['result']
        except KeyError:
            logging.exception('Zabbix Error: {}'.format(response['error']))
            return
