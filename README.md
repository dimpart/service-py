# Service Bots for DIM Network

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/dimpart/service-py/master/LICENSE)
[![Version](https://img.shields.io/badge/alpha-1.0.0-red.svg)](https://github.com/dimpart/service-py/archive/master.zip)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimpart/service-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimpart/service-py/wiki)
[![GitHub Issues](https://img.shields.io/github/issues/dimpart/service-py.svg)](https://github.com/dimpart/service-py/issues)
[![GitHub Forks](https://img.shields.io/github/forks/dimpart/service-py.svg)](https://github.com/dimpart/service-py/network)
[![GitHub Stars](https://img.shields.io/github/stars/dimpart/service-py.svg)](https://github.com/dimpart/service-py/stargazers)

Secure chat services, powered by [DIM-Python](https://github.com/dimchat/demo-py).


## Getting started

### 0. Download source codes and requirements

```shell
cd ~/Documents/
mkdir -p github.com; cd github.com/

# project source codes
mkdir -p dimpart; cd dimpart/
git clone https://github.com/dimpart/service-py.git

# requirements
cd service-py
pip3 install -r requirements.txt

```

### 1. Configurations

Clone ```config.ini```:

```shell
mkdir -p /etc/dim_bots
cd ~/Documents/github.com/dimpart/service-py

cp etc/config.ini /etc/dim_bots/config.ini

vim /etc/dim_bots/config.ini
```

Edit ```config.ini```:

```ini
#
#   Configuration for Bots
#

[database]
# root  = /var/dim
public  = /var/dim/public
private = /var/dim/private

[redis]
# host     = 'localhost'
# port     = 6379
# password = '1234'
# enable   = on

[station]
host = 106.52.25.169
port = 9394

[ans]
tvbox = test_bot@2tyKqx2nPwtYnmf4T3p3mbKwaGfW1fUSpb
sites = test_bot@2tyKqx2nPwtYnmf4T3p3mbKwaGfW1fUSpb

[tvbox]
index = http://tfs.dim.chat/tvbox/index.json

[webmaster]
indexes = /var/dim/protected/webmaster/index.json
```

### 2. Generate accounts

Run command:

```shell
dimid --config=/etc/dim_bots/config.ini generate
```

amd follow these steps:

> Step 1: when the prompt **please input address type** shown, type "4" and enter, this will create a **Bot Account**;

> Step 2: when the prompt **please input ID.name** shown, type "my_bot" and enter;

> Step 3: when the prompt **please input bot name** shown, type any name you want;

> Step 4: when the prompt **please input avatar url** shown, input a URL or enter directly;

After all the steps above done, it would have created a new bot account, you can get the bot ID now.

For example:

```shell
$ dimid generate

[DB] init with config: /etc/dim/config.ini => {...}
!!!         id key path: /var/dim/private/{ADDRESS}/secret.js
!!!       msg keys path: /var/dim/private/{ADDRESS}/secret_keys.js
!!!           meta path: /var/dim/public/{ADDRESS}/meta.js
!!!      documents path: /var/dim/public/{ADDRESS}/documents.js
!!!       contacts path: /var/dim/private/{ADDRESS}/contacts.js
!!!        members path: /var/dim/private/{ADDRESS}/members.js
!!!     assistants path: /var/dim/private/{ADDRESS}/assistants.js
!!! administrators path: /var/dim/private/{ADDRESS}/administrators.js
!!!  group history path: /var/dim/private/{ADDRESS}/group_history.js
Generating DIM account...
--- address type(s) ---
    0: User
    1: Group (User Group)
    2: Station (Server Node)
    3: ISP (Service Provider)
    4: Bot (Business Node)
    5: ICP (Content Provider)
    6: Supervisor (Company President)
    7: Company (Super Group for ISP/ICP)
    8: User (Deprecated)
   16: Group (Deprecated)
  136: Station (Deprecated)
  200: Bot (Deprecated)
>>> please input address type: 4
!!! address type: 4
!!! meta type: 1
>>> please input ID.name (default is "test_bot"): tvbox
!!! ID.name (meta seed): tvbox
!!!
!!! ========================================================================
!!!   Editing document for: tvbox@2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV
!!! ------------------------------------------------------------------------
!!!
>>>   please input bot name (default is "Service Bot"): TV Box
<<<   name = TV Box;
!!!
>>>   please input avatar url (default is ""): 
<<<   avatar = ;
!!!
!!! ------------------------------------------------------------------------
!!!   Done!
!!! ========================================================================
!!!
[2024-09-05 22:11:51] [DB] PrivateKeyStorage >	Saving identity private key into: /var/dim/private/2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV/secret.js
[2024-09-05 22:11:51] [DB] PrivateKeyStorage >	Saving message private keys into: /var/dim/private/2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV/secret_keys.js
[2024-09-05 22:11:51] [DB] MetaStorage >  	    Saving meta into: /var/dim/public/2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV/meta.js
[2024-09-05 22:11:51] [DB] DocumentStorage >	Saving 1 document(s) into: /var/dim/public/2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV/documents.js
!!!
!!! ID: tvbox@2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV
!!!
!!! meta type: 1, document type: visa, name: "TV Box"
!!!
!!! private key: ECC, msg keys: ['RSA']
!!!
```

Now edit ```/etc/dim_bots/config.ini``` and update bot accounts in section **[ans]**:

```
[ans]
tvbox = tvbox@2iwpKywG9EQ37bsJKYz8AMv9rAQh1nGQFV
sites = test_bot@2tyKqx2nPwtYnmf4T3p3mbKwaGfW1fUSpb
```

Do the same steps to get another bot account to update ```ans.sites```.

### 3. Prepare data & run

Create index file for sites:

```
mkdir -p /var/dim/protected/webmaster/
vim /var/dim/protected/webmaster/index.json
```

For example:

```
{
    "china travel": "/var/dim/protected/webmaster/china_travel.md"
}
```

And then edit your site page ```/var/dim/protected/webmaster/china_travel.md```:

```
## Hello world!
This is a page written in markdown format
```

If everything is OK, you should be able to launch your bot now!
