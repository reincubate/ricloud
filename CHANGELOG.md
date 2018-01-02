**2.3.1** - *released 2018-01-02*

* Make the *asmaster* listener similar in design to the interactive *asapi* mode by splitting out the stream consumer to a different thread.
* Move task result processing responsibilities from the stream consumer thread to the main thread. This releases the stream consumer thread from needing wasteful IO operations.
* Some cleanup of tests and initial configuration for CircleCI testing integration.
* A little bit of config and code cleanup.

**2.3.0** - *released 2017-12-14*

* Increase the stream listener's resilience to connectivity interruptions using a simple retry mechanism.
* Report data consumption back to *asapi* when received through the *asmaster* listener. This helps us track whether data is being retrieved correctly.

**2.2.2** - *released 2017-10-24*

* Added live-only datatype sample application. This serves as an example of how to access account wide datatypes such as live browser history or iCloud Photo Library.

**2.2.1** - *released 2017-08-04*

* Added database connection management to asmaster listener implementation.

**2.2.0** - *released 2017-05-18*

* Added support for `reset-subscription-since`
* Fixed escaping file paths

**2.1.1** - *released 2017-05-12*

* Added support for `list-services`
* Fixed setup migration from HTTP GET to POST
* Correctly format output in manager mode as JSON, not serialised Python
* Don't pollute nicely formed JSON errors
* Automatic reconnection of the stream listener
* Automatic creation of log folder
* Added date to log format
* Improved memory use in large MySQL inserts
* Fixed escaping of JSON in feed.body field

**2.1.0** - *released 2017-04-24*

* Added manager mode for use with *asmaster*.
* Added listener mode for use with *aschannel*.
* Added supporting database schema, etc. for listener mode.

**2.0.4** - *released 2017-02-10*

* Improve handling of error responses from *asapi*.
* Little encoding tweak for certain device names.

**2.0.3** - *released 2017-01-20*

* Tweak default task timeout value.
* Minor copy changes.

**2.0.2** - *released 2017-01-19*

* Fix bug submitting 2FA code.
* Updates to README.

**2.0.1** - *released 2017-01-18*

* Fix for pypi package release requirements.

**2.0.0** - *released 2017-01-17*

* Inital release of the new ricloud API client. This implementation is not compatible with implementations of the `1.x.y` versions of the client.

**1.0.13**

* Improved documentation.

**1.0.12**

* Added support for list all devices datatype.

**1.0.11**

* Fixed exception handling.
* Improved information displayed when exceptions called.

**1.0.10**

* Updated documentation.
* Added support for account management features.
* Added support for new data types.
* Improved exception handling.

**1.0.9**

* Add support for iOS 10.

**1.0.8**

* Fixed issue retrieving `photo` withouth permissions.

**1.0.7**

* Fixed documentation issue.

**1.0.6**

* Fixed configuration issue on Windows.

**1.0.5**

* Added more data types (Viber, Kik, Line and Calendar appointments).

**1.0.4**

* Enhanced documentation.

**1.0.3**

* Bigger documentation update.

**1.0.2**

* Documentation update to include more flags.

**1.0.1**

* Support exporting live non-backup contacts.

**1.0.0**

* First release.
