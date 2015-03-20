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
              'session': session,
              'include_pass': False,
              'ca_cert': cacert}

    return heatclient.Client('1', endpoint, **kwargs)
