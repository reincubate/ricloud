# Introduction

## Overview

The Reincubate ricloud API makes the iCloud accessible to investigators, developers and integrators. The API includes functionality for extraction, manipulation and recovery of many types of iOS and app data.

It has functionality to support bulk, scheduled, and realtime data access. It is a PUSH api and makes many commonly accessed forms of data available as JSON feeds.

It fully supports a number of online services. Including Apple iOS 9 and iOS 10 Beta CloudKit-based iCloud backups, and backups created with A9 chipsets: It can provide real-time iCloud data for a number of datatypes, and supports undeletion of content which has been previously erased from the iCloud.

### Who uses the API, and is it secure?

The API is hosted, delivered and developed in the UK and US by Reincubate, makers of the first iOS data extraction product, the [iPhone Backup Extractor](https://www.reincubate.com/labs/iphone-backup-extractor-how-extract-files-iphone-backup-windows/). The company is subject to stringent UK data protection legislation, and is compliant with EU and US Safe Harbor regulations.

Reincubate are trusted by security, LEA and government users around the world. The company publishes a select few testimonials on the API's [product information page](https://www.reincubate.com/ricloud/), and the [enterprise team](mailto:enterprise@reincubate.com) can arrange references for potential users.

Clients put the API to a number of uses, including:

* **Compliance**: connecting corporations with data on their device inventories.
* **CRM and point-of-sale (POS) integration**: connecting stores and sales teams with data on their clients calls and messages.
* **Child protection**: allowing parents to safeguard their childrens' online activity.
* **Law enforcement and forensics**: allowing law enforcement and security agents to access information on devices and accounts of interest.

### What level of data access does the API provide?

For Apple services, the API provides access to all raw iCloud files and data. It also provides access to a number of JSON feeds, use of which is recommended over raw file access.

## What benefits does Reincubate's ricloud API provide?

The API -- and in particular, the feeds -- provide a number of substantial benefits:

 * **Ease of integration**. The API is easy for development teams at any level to work with, and they remove the need for clients to have any highly specialist knowledge about either iCloud / CloudKit storage, or about any third-party apps.

    This benefit is not easily overstated: the complexity of developing and maintaining an interface to the iCloud is substantial, and layered on top of that is the need to support multiple data formats for core iOS data and app files. Not only does iOS use different data formats, but each app (for instance, WhatsApp), uses a set of data formats and structures which can change week-to-week with app updates.

    The API supports all the *"difficult"* features: iOS 9, iOS 10 Beta, CloudKit, iCloud 8 + 9 merging, 2SV/2FA, partial snapshots, tokenisation, A9 & A9X.

 * **Future proofing**. Reincubate is committed to maintaining support for contemporary and past iCloud and iOS data formats, and has a solid track record in this space:
    * *1st* to support iOS data access (2008)
    * *1st* to support encrypted iOS data access (2009)
    * *1st* to support iCloud data extraction (2011)
    * *1st & only* with an API to support [iCloud / CloudKit iOS 9 data access](https://www.reincubate.com/blog/2015/sep/25/extracting-data-ios-9-icloud-backups/) (2015)


 * **Support & access to unrivalled expertise**. As a consequence of the company's focus and positioning as *the app data company*, Reincubate's team have unrivalled experience and knowledge in the field. This experience is particularly valuable for clients exploring new apps and use-cases.

    Users of the JSON feeds are able to take advantage of Reincubate's proprietary techniques in extraction and undeletion of app data, such that the resultant data is more accurate.

 * **Out of the box app support**. Aside from the core iOS datatypes -- *all* of which are supported across *all* iOS versions on *all* devices -- the API has modules to support dozens of third-party apps. Some of the more popular supported apps include WhatsApp, Viber, Kik, WeChat, Line, SnapChat, Facebook Messenger and Skype.

 * **Out of the box developer platform support**. The API has a public open source client implemented in `Python`. And several other implementations available in a number of languages, including `.NET` / `C#` and `JavaScript` available on request.

 * **Speed & scalability**. The Reincubate iCloud API platform is built to scale, and the JSON feed system faster and scales better than raw file access.

 * **Rich feed customisation options**. The feed platform is readily customisable for partner deployments. Examples include `protobuf` format feeds and aggregation of messaging app attachments.

 * **Trust**. Reincubate are trusted by security, LEA and government users around the world. The company is subject to stringent UK data protection legislation, and is compliant with EU and US Safe Harbor regulations.


## Python

Source for this client can be found on GitHub under [ricloud](https://github.com/reincubate/ricloud/).

### Installing the python library.

This tutorial assumes you have python installed and know how to use "[pip](https://en.wikipedia.org/wiki/Pip_(package_manager)" inside a [python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

In a new virtual environment:

   mkvirtualenv myvirtualenv

You can get the ricloud python client using the git clone command:

   git clone git@github.com:reincubate/ricloud.git

And install the necessary dependancies:

   pip install -r requirements.txt

Or by installing the pypy package using pip:

   pip install ricloud


### Configuration

The library is configured by creating a 'ricloud.ini' file in the correct path.

The file should look similar to this:
```
[hosts]
api_host = https://asapi.reincubate.com
stream_host = https://aschannel.reincubate.com

[endpoints]
account_information = /account/
register_account = /register-account/
task_status = /task-status/

[stream]
stream_endpoint = your-aschannel-stream-name-here

[auth]
token = your-ricloud-api-access-token-here

[output]
output_directory = output

[logging]
logs_directory = logs
time_profile = False

[performance]
object_store_greenlets = 50
```

The default ricloud.ini can be found in the 'ricloud' folder of the [repo](https://github.com/reincubate/ricloud/blob/master/ricloud/ricloud.ini).

### Running

From the command line, you can now run:

     python -m ricloud john.appleseed@reincubate.com --password=joshua

For a simple example downloading icloud photos.

Please read the [sample app source](https://github.com/reincubate/ricloud/blob/master/ricloud/applications/icloud_sample.py) for a basic idea of usage or read the full ricloud api docs [here](https://docs.reincubate.com/ricloud/).
