# ricloud: iCloud access made easy

This is a sample Python library for interaction with Reincubate's iCloud API. The Reincubate iCloud API provides powerful programmatic iCloud access to investigators, application developers and integrators. It is RESTful and makes many commonly-accessed forms of data available as JSON feeds.

The API includes functionality for extraction, manipulation and recovery of many types of iOS data, and has functionality to support bulk, scheduled, and realtime data access. It fully supports iOS 9 CloudKit-based iCloud backups, and backups created with the new A9 chipsets.

## JSON feed vs raw file access

There are two core parts to the API: the JSON feed mechanism, and the raw file access mechanism. The JSON feeds come with a number of advantages:

 * Access to feed data is generally faster and scales better than raw file access
 * App data stored in databases and Plists is prone to change in format and location over time; the JSON feed abstracts away that complexity so that you needn't worry.
 * Users of the JSON feeds are able to take advantage of Reincubate's proprietary techniques in extracting app data, such that the resultant data is more accurate.

## Installation

The library can be installed with a single command:

```bash
$ pip install ricloud
```

A sample script is included which provides an example of how the API can be used to access a range of datatypes in a way that is compatible with Apple's 2FA mechanism.

```bash
$ python -c "from ricloud.sample_script import main; main();"
```

### Configuration

The API relies on a set of security credentials, which are stored in an ``ricloud.ini`` file. This package ships with a default configuration file which enables limited access to the API for demonstration purposes. Full access can be gained by contacting [Reincubate](mailto:enterprise@reincubate.com).

The default credentials can be overridden by creating an override file named ``.ricloud.ini`` in the running user's ``HOME`` directory. Alternately, an ``RICLOUD_CONF`` environment variable can be set, specifying the full path and filename of the configuration file.

This file should have the following details:

```yaml
[auth]
# Required and supplied by Reincubate
user =
key =

[test]
# If you want to run automated tests against your account, set these.
user =
key =
apple_id =
password =
```

## Usage

### Authentication against the API and listing iCloud data

```python
from ricloud.api import RiCloud

api = RiCloud()

# Login to iCloud. If you have two factor authentication enabled then you'll need
# submit a challenge request and a response. Have a look at the sample_script.py
# file for an example of this.
api.login(APPLE_ID, APPLE_PASSWORD)

# Now we have a list of the devices connected to this account stored in `api.devices`
# Let's have a look:
print api.devices
```

### Using the JSON feed API

The API is able to return data retrieved from a wide range of apps, and enumerations for some of these are baked into the sample API. However, we have many other types of app feeds available, including Viber, Kik, WeChat, Line, and others.

> We also have functionality such as message undeletion which can be enabled on demand against API keys.

To choose which data types to return in the feed, users can pass a mask of data types to the `BackupClient.request_data` method. To select multiple data types, separate each type with the bitwise OR ``|`` operator. For example to select both SMS and photo data:

```python
# SMS and photo retrieval
requested_data = BackupClient.DATA_SMS | BackupClient.DATA_PHOTOS
```

If no selection is made, the API will return all available data available. The following is an example of how to select which data to retrieve.

#### Device-specific iOS data

```python
# For Message (SMS, MMS, iMessage) retrieval
requested_data = BackupClient.DATA_SMS

# For photo retrieval
requested_data = BackupClient.DATA_PHOTOS

# For browser history retrieval
requested_data = BackupClient.DATA_BROWSER_HISTORY

# For call history retrieval
requested_data = BackupClient.DATA_CALL_HISTORY

# For list of installed apps
requested_data = BackupClient.DATA_INSTALLED_APPS

# For device contact retrieval
requested_data = BackupClient.DATA_CONTACTS
```

#### iCloud account-specific data

```python
# For iCloud contact retrieval
requested_data = BackupClient.DATA_WEB_CONTACTS

# For location retrieval
requested_data = BackupClient.DATA_WEB_LOCATION
```

#### App-specific data

```python
# For WhatsApp message retrieval
requested_data = BackupClient.DATA_WHATSAPP_MESSAGES

# For Skype message retrieval
requested_data = BackupClient.DATA_SKYPE_MESSAGES
```

#### Simple sample script

Putting this all together, a simple script to access iCloud data as a JSON feed looks like this:

```python
from datetime import datetime
import json

from ricloud.api import RiCloud
from ricloud.backup import BackupClient

api = RiCloud()

# Login to iCloud. If you have two factor authentication enabled then you'll need
# submit a challenge request and a response. Have a look at the sample_script.py
# file for an example of this.
api.login(APPLE_ID, APPLE_PASSWORD)

# Now we have a list of the devices connected to this account stored in `api.devices`
# For this sample script, let's just look at the first device
device = api.devices.keys()[0]

# Build a bit mask of the data we want to access. If you don't set this then the
# API will supply all the information your account has access to.
data_types = BackupClient.DATA_SMS | BackupClient.DATA_INSTALLED_APPS

# Ask for any new data since the Jan 1st 2015. If you don't supply this, the API
# will return ALL data available.
since = datetime(2015, 1, 1)

# Fire the request
data = api.backup_client.request_data(device, data_mask=data_types, since=since)

# Print the output to console
print json.dumps(data, indent=2)

# Let's get any attachments which have been referenced by the messages
# The arguments for `download_file` are the `device_id` to download from
# and the `file_id`.
for sms in data['sms']:
    for attachment in sms['attachments']:
        with open(attachment['filename'], 'wb') as out:
            api.backup_client.download_file(device, attachment['file_id'], out)
```

### Using the raw file access API

The raw file access API is available for downloading message attachments, or
directly downloading more esoteric files from the iCloud.

> As noted above, it is invariably better to use the JSON feeds when working with app data. The JSON feeds provide faster and more accurate data access.

The `BackupClient.download_file` method takes a ``file_id``, ``device_id`` and a
file handle to write the file to. `file_id`s are built from SHA-1 hashes of a
file's AppDomain and filename.

```python
out = open(filename, 'wb')
api.backup_client.download_file(device_id, file_id, out)
```

#### Sample `file_id`s

Common hash keys associated with apps for direct file access include the following.

* SMS: `3d0d7e5fb2ce288813306e4d4636395e047a3d28`
* WhatsApp: `1b6b187a1b60b9ae8b720c79e2c67f472bab09c0`, `1c6a49018bcace96656e4fe8f08d572ce071b92c`, `7c7fba66680ef796b916b067077cc246adacf01d`
* Viber: `b39bac0d347adfaf172527f97c3a5fa3df726a3a`
* Kik: `8e281be6657d4523710d96341b6f86ba89b56df7`

## Troubleshooting

### The JSON feed returns a message: "Contact enterprise@reincubate.com for access to this data"

This message will be returned when the demonstration key is used. Please contact us for a trial key with access to more data. If you already have a trial key, are you correctly specifying it in your `~/.ricloud.ini` file? Note that the file has a period at the start.

## Need more functionality?

Reincubate builds world class iOS and app data access and recovery technology. The company was founded in 2008 and was first to market with iOS backup extraction technology, consumer backup decryption, and more recently with enterprise iCloud support. Clients include law enforcement, government and security organisations in the US and internationally, and to corporations as large as Microsoft and IBM.

> Users with simpler needs may wish to try the [iPhone Backup Extractor](<http://www.iphonebackupextractor.com), which provides a set of iCloud functionality better suited to consumers.

With six years' experience helping police forces, law firms and forensics labs access iOS data, the company can help enterprise users with:

* iCloud access and data recovery
* Recovery of data deleted from SQLite databases
* Bulk iOS data recovery
* Forensic examination of iOS data
* Passcode, password and keybag analysis
* Custom iOS app data extraction
* Advanced PList, TypedStream and Mbdb manipulation

Contact [Reincubate](mailto:enterprise@reincubate.com) for more information, or see our site at [reincubate.com](https://www.reincubate.com).

## Terms & license

Users must not use the API in any way that is unlawful, illegal, fraudulent or harmful; or in connection with any unlawful, illegal, fraudulent or harmful purpose or activity. See the `LICENSE` file. Full terms are available from [Reincubate](mailto:enterprise@reincubate.com).

Copyright &copy; Reincubate Ltd, 2011 - 2015, all rights reserved.
