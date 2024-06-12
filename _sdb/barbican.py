'''
SDB module for Barbican
 
Like all sdb modules, the Barbican module requires a configuration profile
to be configured in either the minion or, as in our implementation,
in the master configuration file (/etc/salt/master.d/passwords.conf).
This profile requires:
 
.. code-block:: yaml
 
    pwd:
        driver: barbican
        auth_url: 'https://auth.cloud.ovh.net/v3'
        username: 'user-xxxxxxxxxxxx'
        user_domain_name: 'Default'
        password: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        project_name: 'xxxxxxxxxxxxxxxxx'
        project_domain_name: 'Default'
 
The ``driver`` refers to the Barbican module and ``auth_url`` ``username`` ``user_domain_name`` ``password`` ``project_name`` ``project_domain_name`` is the parametre 
to the Barbican backend connection that contains the data.

This file should be saved as salt/_sdb/barbican.py
 
.. code-block:: yaml

     user: sdb://pwd/user1
 
CLI Example:
 
.. code-block:: bash
 
     salt-run sdb.delete sdb://pwd/user1
     salt-run sdb.get sdb://pwd/user1
     salt-run sdb.set sdb://pwd/user1 '$5$0DZt7BTf$gjNPsFCJDpwUhLervVkOhbzrmSxNnfJw46V.h7eEaE.'
'''

import logging

from keystoneclient.auth import identity
from keystoneauth1 import session
from barbicanclient import client

import salt.exceptions
import salt.utils.files
 
log = logging.getLogger(__name__)

__func_alias__ = {
    'set_': 'set'
}


def barbican_connection(func):
    def get_value_or_raise_error(profile, key, default=None):
        value = profile.get(key, default)
        if value is None:
            raise salt.exceptions.CommandExecutionError(
                f'No key {key} in the profile')
        return value

    def wrapper(*args, **kwargs):
        profile = kwargs['profile']

        auth = identity.v3.Password(
            auth_url = get_value_or_raise_error(profile, 'auth_url'),
            username = get_value_or_raise_error(profile, 'username'),
            user_domain_name = get_value_or_raise_error(profile, 'user_domain_name'),
            password = get_value_or_raise_error(profile, 'password'),
            project_name = get_value_or_raise_error(profile, 'project_name'),
            project_domain_name = get_value_or_raise_error(profile, 'project_domain_name'),
            )

        sess = session.Session(auth=auth)
        barbican = client.Client(session=sess)
        kwargs['barbican'] = barbican  
        kwargs['profile'] = profile
        return func(*args, **kwargs)
    
    return wrapper


@barbican_connection
def delete(key, profile=None, barbican=None):
    '''
    Remove a last key of barbican 
    '''
    secrets = barbican.secrets.list(name=key)
    if len(secrets) == 0:
        return False
    
    return key

@barbican_connection
def get(key, profile=None, barbican=None):
    '''
    Get a value from a Barbican
    '''
    secrets = barbican.secrets.list(name=key)
    if len(secrets) == 0:
        return {}

    return sorted(secrets, key=lambda x: x.created)[-1].payload

@barbican_connection
def set_(key, value, profile=None, barbican=None):
    '''
    Set a new value key/value with barbican
    '''
    secrets = barbican.secrets.list(name=key)

    if not len(secrets) == 0:
        msg = f"the key {key} is already taken."
        log.warning(msg)
        return False

    secret = barbican.secrets.create(name=key,
                            payload=value)
    secret.store()
    
    return secret.payload
