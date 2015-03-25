# Copyright 2015 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from heatclient import client as heatclient
from keystoneclient.auth.identity import v2
from keystoneclient import session

LOG = logging.getLogger(__name__)


def get_heat_client(username, password, tenant_name, auth_url, cacert=None,
                    region_name='regionOne'):
    LOG.debug('Creating Keystone session to fetch Heat endpoint.')
    auth = v2.Password(auth_url=auth_url, username=username, password=password,
                       tenant_name=tenant_name)
    ks_session = session.Session(auth=auth)
    endpoint = ks_session.get_endpoint(service_type='orchestration',
                                       interface='public',
                                       region_name=region_name)
    LOG.debug('Creating heat client.')

    kwargs = {'username': username,
              'password': password,
              'tenant_name': tenant_name,
              'auth': auth,
              'auth_url': auth_url,
              'session': ks_session,
              'include_pass': False,
              'ca_cert': cacert}

    return heatclient.Client('1', endpoint, **kwargs)
