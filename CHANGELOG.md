**3.1.0** - *released 2020-02-03*

* Update iCloud sample commands to be more modular.
* Add iCloud sample commands for downloading poll results. This includes cascading polls to get files referenced in retrieved JSON data.
* Fix result resource ack action.
* Change iCloud sample to abort on task timeout.
* Flask sample webhook receiver review.

**3.0.1** - *released 2019-10-11*

* Quickfix for requests module.

**3.0.0** - *released 2019-10-11*

* Implement await response mechanism. This can be configured via the `await_for` setting under the `api` section of the ricloud configuration file.
* Rename `events` client module to `webhooks`.
* Fix for storage and webhook config test calls.
* Start passing client details in User-Agent header.

**3.0.0rc3** - *released 2019-10-03*

* Fix for config viewing cli command.
* Added helper command to retrieve latest *rirelay* subscription poll.
* Fix encoding handling when outputting resource JSON to console.

**3.0.0rc2** - *released 2019-10-02*

* Quickfix for sample commands.

**3.0.0rc1** - *released 2019-10-02*

* Added support for interacting with subscription resources.
* New *rirelay* service samples.
* New helpers commands for local configuration initialisation.
* New helpers for setting up a local event notification receiver using flask and a tool such as ngrok.

**2.3.10** - *released 2019-03-14*

* Use sessions to improve connection efficiency in API calls.
* Clear critical path in asmaster file handler. This helps the listener thread consume the stream faster by a few orders of magnitude.
* Minor logging of pending result handling added.
* Some extra profiling for asmaster handlers.

**3.0.0rc0** - *released 2019-01-15*

* Initial release of *ricloud-py* for the ricloud v3 API. This implementation is not compatible with older versions of the API. See the API docs for more information on new features in the ricloud v3 API.

**2.3.9** - *released 2018-12-11*

* Improve *asmaster* listener to allow simpler configuration of custom result handlers.

**2.3.8** - *released 2018-11-01*

* Update version of requests in requirements due to vulnerability discovery.
* Decouple database handler from core code to make requirement of MySQL dependencies optional.
* Minor fixes and code cleanup.

**2.3.7** - *released 2018-06-01*

* Fix use of non-public pip utility.

**2.3.6** - *released 2018-02-21*

* Add dedicated handler for temporary files.
* Fix bug where the client in listener mode would hold onto partially complete files forever in case of connection issues. This could lead to the client using a large amount of disk space for corrupted files.

**2.3.5** - *released 2018-01-11*

* Quickfix for listener stream thread exception handling and lifetime management.

**2.3.4** - *released 2018-01-11*

* Tweaks to listener worker and stream threads. This makes them less resources hungry and more reliable.
* Add status command for a quick overview of the latest occurrences of key messages in the log.

**2.3.3** - *released 2018-01-04*

* Slight modification to component responsibilities. This gives us better oversight over the state of the stream listener thread.
* Simplify Stream interface, add logging, and minor code improvements elsewhere.

**2.3.2** - *released 2018-01-03*

* Improved the robustness of the new worker thread when in *asmaster* listener mode. Extra logging around errors here.
* Extra debug logging around the *asmaster* listener to aid in issue diagnosis.
* Complete setting up CircleCI testing.
* Some nice badges in the README.

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
