"""ricloud API Client.

Usage:
    ricloud <account> [--password=<password>] [--timeout=<timeout>]
    ricloud --listen [--timeout=<timeout>]
    ricloud --list-subscriptions <service> [--timeout=<timeout>]
    ricloud --subscribe-account <username> <password> <service> [--timeout=<timeout>]
    ricloud --perform-2fa-challenge <account_id> <device_id> [--timeout=<timeout>]
    ricloud --submit-2fa-challenge <account_id> <code> [--timeout=<timeout>]
    ricloud --resubscribe-account <account_id> <password> [--timeout=<timeout>]
    ricloud --unsubscribe-account <account_id> [--timeout=<timeout>]
    ricloud --list-devices <account_id> [--timeout=<timeout>]
    ricloud --subscribe-device <account_id> <device_id> [--timeout=<timeout>]
    ricloud --unsubscribe-device <account_id> <device_id> [--timeout=<timeout>]
    ricloud --help


Information:
    ricloud can be run in three modes:

    Listen mode:
        Starts a process which listends to feeds, system messages, and files being sent from asmaster, and saves these in the ricloud database.
        ricloud --listen [--timeout=<timeout>]

    Manager mode:
        To send messages to asmaster, such as to register a new account.
        The following actions are available with this mode:
            --list-subscriptions, --subscribe-account, --perform-2fa-challenge, --submit-2fa-challenge, --resubscribe-account, --unsubscribe-account, --list-devices, --subscribe-device, --unsubscribe-device

    Legacy interactive mode:
        For logging in to and downloading data from an account using with, without registering the account with asmaster (and without the corresponding locking prevention).
        ricloud <account> [--password=<password>] [--timeout=<timeout>]


Options:
    -h --help               Show this screen.
    --password=<password>   The password for this account.
    --timeout=<timeout>     How long should we wait for tasks to complete, in seconds. (default: 600s or 10 minutes)

"""


from __future__ import unicode_literals

import logging
from docopt import docopt

from .ricloud import RiCloud
from .conf import DEFAULT_LOG, LOGGING_LEVEL
from .asmaster_api import AsmasterApi
from .utils import select_service, select_samples


def _parse_input_arguments(arguments):
    timeout = int(arguments.get('--timeout') or 600)

    if arguments['--listen']:
        return {
            'mode': 'listen',
            'timeout': timeout,
        }

    manager_mode_actions = [
        'list-subscriptions',
        'subscribe-account',
        'perform-2fa-challenge',
        'submit-2fa-challenge',
        'resubscribe-account',
        'unsubscribe-account',
        'list-devices',
        'subscribe-device',
        'unsubscribe-device',
    ]

    for action in manager_mode_actions:
        if arguments["--{}".format(action)]:
            return {
                'mode': 'manager',
                'timeout': timeout,
            }

    account = arguments['<account>']
    password = arguments['--password']

    return {
        'mode': 'interactive',
        'account': account,
        'password': password,
        'timeout': timeout,
    }


def main():
    # Get input arguments from command line
    arguments = docopt(__doc__)

    # Format the input arguments for the application
    application_payload = _parse_input_arguments(arguments)

    # setup the logger
    logging.basicConfig(filename=DEFAULT_LOG,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=LOGGING_LEVEL)

    if application_payload['mode'] == 'interactive':
        # Main RiCloud object
        ricloud = RiCloud()

        # The RiCloud client retrieves a list of available services from the API.
        service_name = select_service(ricloud)

        # Each service has a client which contains all the available tasks.
        # Sample applications for these clients can be found in the `samples` folder.
        Application = select_samples(ricloud, service_name, application_payload)

        # Execute the application's main function.
        Application.run()

    elif application_payload['mode'] == 'listen':
        # asmaster listener requires MySQLdb, and we want to avoid requiring that otherwise
        from .asmaster_listener import AsmasterListener

        # This sets the listener running and will not return
        AsmasterListener(application_payload['timeout'])

    elif application_payload['mode'] == 'manager':
        api = AsmasterApi(application_payload['timeout'])
        api.setup()

        if(arguments["--list-subscriptions"]):
            print api.list_subscriptions(arguments['<service>'])
        if(arguments["--subscribe-account"]):
            print api.subscribe_account(
                arguments['<username>'],
                arguments['<password>'],
                arguments['<service>'])
        if(arguments["--perform-2fa-challenge"]):
            print api.perform_2fa_challenge(arguments['<account_id>'], arguments['<device_id>'])
        if(arguments["--submit-2fa-challenge"]):
            print api.submit_2fa_challenge(arguments['<account_id>'], arguments['<code>'])
        if(arguments["--resubscribe-account"]):
            print api.resubscribe_account(arguments['<account_id>'], arguments['<password>'])
        if(arguments["--unsubscribe-account"]):
            print api.unsubscribe_account(arguments['<account_id>'])
        if(arguments["--list-devices"]):
            print api.list_devices(arguments['<account_id>'])
        if(arguments["--subscribe-device"]):
            print api.subscribe_device(arguments['<account_id>'], arguments['<device_id>'])
        if(arguments["--unsubscribe-device"]):
            print api.unsubscribe_device(arguments['<account_id>'], arguments['<device_id>'])

if __name__ == '__main__':
    main()
