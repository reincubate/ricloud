# ricloud-py: iCloud access made easy

This is the sample Python client for Reincubate's [iCloud API](https://www.reincubate.com/labs/icloud-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

> Refer to the comprehensive [iCloud API documentation](https://www.reincubate.com/contact/support/icloud-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) for a fuller picture of the API's capabilities, specifications, and benefits.

## Installation

The library can be installed with a single command:

```bash
$ pip install ricloud
```

### Configuration

The API relies on a set of security credentials, which are stored in an ``ricloud.ini`` file. This package ships with a default configuration file which enables limited access to the API for demonstration purposes.

The default credentials can be overridden by creating an override file named ``.ricloud.ini`` in the user's ``HOME`` directory. Alternately, a ``RICLOUD_CONF`` environment variable can be set, specifying the full path and filename of the configuration file.

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

A sample script is included which provides an example of how the API can be used to access a range of datatypes in a way that is compatible with Apple's 2FA mechanism.

To run the sample script, execute the following command:

```bash
$ python -c "from ricloud.sample_script import main; main();"
```

A sample output of the sample script is provided.

```
Please enter your Apple ID: renate@reincubate.com
Please enter your password:

2FA has been enabled, choose a trusted device:
0 - ********16
1 - Renate's iPad - iPad Pro
2 - Renate's iPhone - iPhone 6s

Choose a device by specifying its index (e.g. 0): 2

A code has been sent to your device.
Code:  4967

Your devices:
0 - Renate's iPad [model: J71AP, colour: #3b3b3c, latest-backup: 2015-06-23 07:00:00.000000]
1 - Renate's iPhone [model: N71mAP, colour: #e4e7e8, latest-backup: 2015-10-13 19:07:48.000000]
2 - Renate's iPad [model: J98aAP, colour: #e1e4e3, latest-backup: 2015-11-15 20:36:48.000000]
3 - Renate's iPhone [model: N71AP, colour: #e4e7e8, latest-backup: 2015-11-17 20:51:36.000000]
4 - Renate's US iPhone [model: N49AP, colour: #3b3b3c, latest-backup: 2015-05-06 07:00:00.000000]
5 - Renate's iPhone [model: N61AP, colour: #e1e4e3, latest-backup: 2015-10-21 15:53:26.000000]

Choose a device by specifying its index (e.g. 0): 3

What would you like to download?

1       Messages
2       Photos and Videos
4       Browser History
8       Call History
16      Contacts
32      Installed Apps
512     WhatsApp Messages
1024    Skype Messages
2048    Appointments
4096    Line Messages
8192    Kik Messages
16384   Viber Messages
64      Contacts (live)
256     Location (live)
32768   Facebook Messages
65536   WeChat Messages
131072  Snapchat Messages
262144  Available File list
524288  Browser History (live)
1048576 WhatsApp call logs
2097152 Viber call logs
4194304 App/Device usage data
8388608 Notes

Mask (0) for all:  0
Complete! All data is in the directory "out".
```

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

That `api.devices` dictionary contains data in this format:

```python
{u'7c7fba66680ef796b916b067077cc246adacf01d': {
    u'colour': u'#e4e7e8',
    u'device_name': u"Renate's iPhone",
    u'latest-backup': u'2016-03-17 16:46:39.000000',
    u'model': u'N71mAP',
    u'name': u'iPhone 6s'},
 u'8e281be6657d4523710d96341b6f86ba89b56df7': {
    u'colour': u'#e1e4e3',
    u'device_name': u"Renate's iPad",
    u'latest-backup': u'2016-03-13 19:35:52.000000',
    u'model': u'J98aAP',
    u'name': u'iPad Pro'},
}
```

In the `api.devices` dictionary, the keys are device ids of the devices associated with the iCloud account.

### Using the JSON feed API

The API is able to retrieve data from a wide range of apps; a list is provided below.

> Functionality such as message undeletion can be enabled on demand against API keys.

To request a data type, users can pass a mask of data types to the `BackupClient.request_data` method. To select multiple data types, separate each type with the bitwise OR ``|`` operator. For example to select both SMS and photo data:

```python
# SMS and photo retrieval
requested_data = BackupClient.DATA_SMS | BackupClient.DATA_PHOTOS
```

If no selection is made, the API will return all available data available.

The following is a complete list of the bit-flags that can be passed to `BackupClient.request_data`.

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

# For appointment retrieval
requested_data = BackupClient.DATA_APPOINTMENTS

# For App usage retrieval
requested_data = BackupClient.DATA_APP_USAGE

# For Notes retrieval
requested_data = BackupClient.DATA_NOTES

# For list of files associated to a device
requested_data = BackupClient.DATA_FILE_LIST

# For live Web browser history retrieval
requested_data = BackupClient.DATA_WEB_BROWSER_HISTORY
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

# For WhatsApp call history retrieval
requested_data = BackupClient.DATA_WHATSAPP_CALL_HISTORY

# For Skype message retrieval
requested_data = BackupClient.DATA_SKYPE_MESSAGES

# For Facebook message retrieval
requested_data = BackupClient.DATA_FACEBOOK_MESSAGES

# For Snapchat message retrieval
requested_data = BackupClient.DATA_SNAPCHAT_MESSAGES

# For Viber message retrieval
requested_data = BackupClient.DATA_VIBER_MESSAGES

# For Viber call history
requested_data = BackupClient.DATA_VIBER_CALL_HISTORY

# For Line message retrieval
requested_data = BackupClient.DATA_LINE_MESSAGES

# For Kik message retrieval
requested_data = BackupClient.DATA_KIK_MESSAGES

# For Wechat message retrieval
requested_data = BackupClient.DATA_WECHAT_MESSAGES
```

#### Simple sample script

We can combine the ideas above to write a simple script to access iCloud data via the JSON feed.

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

## Troubleshooting

See the iCloud API [support page](https://www.reincubate.com/contact/support/icloud-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

## <a name="more"></a>Need more functionality?

Reincubate's vision is to provide data access, extraction and recovery technology for all app platforms - be they mobile, desktop, web, appliance or in-vehicle.

The company was founded in 2008 and was first to market with both iOS and iCloud data extraction technology. With over half a decade's experience helping law enforcement and security organisations access iOS data, Reincubate has licensed software to government, child protection and corporate clients around the world.

The company can help users with:

* iCloud access and data recovery
* Recovery of data deleted from SQLite databases
* Bulk iOS data recovery
* Forensic examination of iOS data
* Passcode, password, keybag and keychain analysis
* Custom iOS app data extraction
* Advanced PList, TypedStream and Mbdb manipulation

Contact [Reincubate](https://www.reincubate.com/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) for more information.

## Terms & license

See the `LICENSE.md` file for details on this implentation's license. Users must not use the API in any way that is unlawful, illegal, fraudulent or harmful; or in connection with any unlawful, illegal, fraudulent or harmful purpose or activity.
