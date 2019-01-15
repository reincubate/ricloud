# ricloud-py: iCloud access made easy

[![pypi](https://img.shields.io/pypi/v/ricloud.svg)](https://pypi.python.org/pypi/ricloud)
[![CircleCI](https://circleci.com/gh/reincubate/ricloud.svg?style=shield)](https://circleci.com/gh/reincubate/ricloud)
[![docs](https://img.shields.io/badge/docs-ricloud-blue.svg)](https://docs.reincubate.com/ricloud/)

This is the Python client for *ricloud*, Reincubate's [Cloud Data API](https://reincubate.com/labs/icloud-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

> Refer to the comprehensive *ricloud* [documentation](https://docs.reincubate.com/ricloud-v3/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) for a fuller picture of the API's capabilities, specifications, and benefits. See also the [Apple iCloud service](https://docs.reincubate.com/ricloud/icloud-backups/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) documentation for its rich capabilities in accessing iCloud data.

## Installation

The library can be installed with a single command:

```bash
$ pip install ricloud==3.0.0rc0
```

Note the version is specified explicitly above, that is because this version is currently in beta.

## Usage

A sample script is included which provides an example of how the API can be used to access a range of datatypes in a way that is compatible with Apple's 2FA mechanism.

Before you can start using the API you will need to get setup with an access token. More details on getting started with the API can be found [in the docs](https://docs.reincubate.com/ricloud-v3/getting-started/#getting-started).

To run the sample script in interactive mode, execute the following command:

```bash
$ ricloud samples icloud john.appleseed@reincubate.com
```

More details on how to use the *ricloud-py* client can be found in [our docs](https://docs.reincubate.com/ricloud-v3/ricloud-py/).

## Troubleshooting

See the [support & service status](https://docs.reincubate.com/ricloud/status/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) page.

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

See the `LICENSE.md` file for details on this implementation's license. Users must not use the API in any way that is unlawful, illegal, fraudulent or harmful; or in connection with any unlawful, illegal, fraudulent or harmful purpose or activity.
