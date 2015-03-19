import logging

import glanceclient
from ironicclient import client as ironicclient
from keystoneclient.auth.identity import v2
from keystoneclient import session
from keystoneclient.v2_0 import client as ksclient
from keystoneclient.v3 import client as ks3client
from neutronclient.neutron import client as neutronclient
from novaclient.extension import Extension
from novaclient.v1_1 import client as novav11client
from heatclient import client as heatclient
from novaclient.v1_1.contrib import baremetal

LOG = logging.getLogger(__name__)


def get_nova_bm_client(username, password, tenant_name, auth_url, cacert=None):
    LOG.debug('Creating nova client.')
    baremetal_extension = Extension('baremetal', baremetal)
    return novav11client.Client(username,
                                password,
                                tenant_name,
                                auth_url,
                                extensions=[baremetal_extension],
                                cacert=cacert)


def get_ironic_client(username, password, tenant_name, auth_url, cacert=None):
    LOG.debug('Creating ironic client.')
    kwargs = {'os_username': username,
              'os_password': password,
              'os_auth_url': auth_url,
              'os_tenant_name': tenant_name,
              'ca_file': cacert}

    return ironicclient.get_client(1, **kwargs)


def get_keystone_client(username,
                        password,
                        tenant_name,
                        auth_url,
                        cacert=None):

    LOG.debug('Creating keystone client.')
    kwargs = {'username': username,
              'password': password,
              'tenant_name': tenant_name,
              'auth_url': auth_url,
              'cacert': cacert}

    return ksclient.Client(**kwargs)


def get_keystone_v3_client(username,
                           password,
                           tenant_name,
                           auth_url,
                           cacert=None):

    LOG.debug('Creating keystone v3 client.')
    kwargs = {'username': username,
              'password': password,
              'tenant_name': tenant_name,
              'auth_url': auth_url.replace('v2.0', 'v3'),
              'cacert': cacert}

    return ks3client.Client(**kwargs)


def get_neutron_client(username,
                       password,
                       tenant_name,
                       auth_url,
                       cacert=None):
    LOG.debug('Creating neutron client.')
    kwargs = {'username': username,
              'password': password,
              'tenant_name': tenant_name,
              'auth_url': auth_url,
              'ca_cert': cacert}

    neutron = neutronclient.Client('2.0', **kwargs)
    neutron.format = 'json'
    return neutron


def get_heat_client(username, password, tenant_name, auth_url, cacert=None,
                      region_name='regionOne'):
    LOG.debug('Creating Keystone session to fetch Heat endpoint.')
    auth = v2.Password(auth_url=auth_url, username=username, password=password,
                       tenant_name=tenant_name)
    ks_session = session.Session(auth=auth)
    endpoint = ks_session.get_endpoint(service_type='orchestration',
                                       interface='public',
                                       region_name=region_name)
    token = ks_session.get_token()
    LOG.debug('Creating heat client.')

    kwargs = {'username': username,
              'password': password,
              'tenant_name': tenant_name,
              'auth': auth,
              'auth_url': auth_url,
              'session': session,
              'include_pass': False,
              'ca_cert': cacert}

    return heatclient.Client('1', endpoint, **kwargs)


def get_glance_client(username, password, tenant_name, auth_url, cacert=None,
                      region_name='regionOne'):
    LOG.debug('Creating Keystone session to fetch Glance endpoint.')
    auth = v2.Password(auth_url=auth_url, username=username, password=password,
                       tenant_name=tenant_name)
    ks_session = session.Session(auth=auth)
    endpoint = ks_session.get_endpoint(service_type='image',
                                       interface='public',
                                       region_name=region_name)
    token = ks_session.get_token()
    LOG.debug('Creating glance client.')
    return glanceclient.Client('1', endpoint=endpoint, token=token,
                               cacert=cacert)
