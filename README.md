[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)

![](images/saltstack_horizontal_dark.png?raw=true)

# SDB interface for manage passwords password with Barbican

The SaltStack SDB (Simple Data Base) interface is designed to store and retrieve data that, unlike pillars and grains, is not necessarily minion-specific. It is a generic database interface for SaltStack. 

We will show here how you can make use of SDB for storing and retrieving passwords in a centralized way with Barbican vault.

## Prerequisites before use

### Dependencies

```
keystoneauth1 ~= 4.4.0
python-keystoneclient ~= 4.4.0
python-barbicanclient  ~= 5.2.0
```

### SDB Configuration

Add the configuration inside the file password configuration of salt
best pratique for the configuration is to use the `master.d/<custom_config>.conf`

update the configuration salt.

/etc/salt/master.d/module_path.conf

```conf
# Add any additional locations to look for master runners:
runner_dirs: 
  - /srv/salt/_sdb

file_roots:
  base:
    - /srv/salt
```

### Add Barbican plugin

The barbican plugin can by add in the folder `/srv/salt/_sdb/`

Synchronize the module with salt

```bash
salt-run saltutil.sync_all
```

`/etc/salt/master.d/passwords.conf`

```conf
pwd:
    driver: barbican
    auth_url: 'https://auth.cloud.ovh.net/v3'
    username: 'user-xxxxxxxxxxxx'
    user_domain_name: 'Default'
    password: 'xxxxxxxxxxxxxxxxxxx'
    project_name: 'xxxxxxxxxx'
    project_domain_name: 'Default'

```

The driver need to have the same name of the plugin file in `_sdb` directory.

# Example with cli salt

```bash
salt-run sdb.set sdb://pwd/user1 'hello world'

salt-run sdb.get sdb://pwd/user1

salt-run sdb.delete sdb://pwd/user1

```

# Issue

When i import my plugin it not fonded i things this because in the context the dependencies are not installed in the python environnement of salt cli...
