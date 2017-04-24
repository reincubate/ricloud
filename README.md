# ricloud-py: iCloud access made easy

This is the sample Python client for *ricloud*, Reincubate's [Cloud Data API](https://www.reincubate.com/ricloud-cloud-data-api/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

> Refer to the comprehensive *ricloud* [documentation](https://docs.reincubate.com/ricloud/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) for a fuller picture of the API's capabilities, specifications, and benefits. See also the [Apple iCloud service](https://docs.reincubate.com/ricloud/icloud-backups/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) documentation for its rich capabilities in accessing iCloud data.

## Installation

The library can be installed with a single command:

```bash
$ pip install ricloud
```

## Usage

A sample script is included which provides an example of how the API can be used to access a range of datatypes in a way that is compatible with Apple's 2FA mechanism.

To run the sample script in interactive mode, execute the following command:

```bash
$ python -m ricloud john.appleseed@reincubate.com --password=joshua
```

*ricloud*'s [Python quickstart documentation](https://docs.reincubate.com/ricloud/python-quickstart/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud) covers in detail the other modes in which this sample client can be used.

For a simple tutorial on downloading photos from the iCloud, please see the [tutorial](https://docs.reincubate.com/ricloud/tutorials/icloud-photos/?utm_source=github&utm_medium=ricloud-py&utm_campaign=ricloud).

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
