# ricloud-py: iCloud access made easy

This is the sample Python client for Reincubate's [iCloud API](https://www.reincubate.com/labs/icloud-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

> Refer to the comprehensive [iCloud API documentation](https://docs.reincubate.com/ricloud/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) for a fuller picture of the API's capabilities, specifications, and benefits.

## Installation

The library can be installed with a single command:

```bash
$ pip install ricloud
```

### Configuration

The API relies on a set of security credentials, which are stored in an ``ricloud.ini`` file. This package ships with a default configuration file which enables limited access to the API for demonstration purposes.

The default credentials can be overridden by creating an override file named ``.ricloud.ini`` in the user's ``HOME`` directory. Alternately, a ``RICLOUD_CONF`` environment variable can be set, specifying the full path and filename of the configuration file.


```yaml
[hosts]
api_host = https://asapi.reincubate.com
stream_host = https://aschannel.reincubate.com

[endpoints]
account_information = /account/
register_account = /register-account/
task_status = /task-status/

[stream]
# Required and supplied by Reincubate
stream_endpoint = your-aschannel-stream-name-here

[auth]
# Required and supplied by Reincubate
token = your-ricloud-api-access-token-here

[output]
output_directory = output

[logging]
logs_directory = logs
time_profile = False

[performance]
object_store_greenlets = 50
```

The default `ricloud.ini` can be found in [this repository](https://github.com/reincubate/ricloud/blob/master/ricloud/ricloud.ini).

## Usage

A sample script is included which provides an example of how the API can be used to access a range of datatypes in a way that is compatible with Apple's 2FA mechanism.

To run the sample script, execute the following command:

```bash
$ python -m ricloud john.appleseed@reincubate.com --password=joshua
```

For a simple tutorial on downloading photos from the iCloud, please see the [tutorial](https://docs.reincubate.com/ricloud/Tutorials/icloud-tutorial-00/).

## Troubleshooting

See the iCloud API [documentation & support page](https://docs.reincubate.com/ricloud/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

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
