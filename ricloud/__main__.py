"""ricloud API Client.

Usage:
    ricloud status
    ricloud <account> [--password=<password>] [--timeout=<timeout>]
    ricloud --listen [--timeout=<timeout>]
    ricloud --list-services [--timeout=<timeout>]
    ricloud --list-subscriptions <service> [--timeout=<timeout>]
    ricloud --subscribe-account <username> <password> <service> [--timeout=<timeout>]
    ricloud --perform-2fa-challenge <account_id> <device_id> [--timeout=<timeout>]
    ricloud --submit-2fa-challenge <account_id> <code> [--timeout=<timeout>]
    ricloud --resubscribe-account <account_id> <password> [--timeout=<timeout>]
    ricloud --unsubscribe-account <account_id> [--timeout=<timeout>]
    ricloud --list-devices <account_id> [--timeout=<timeout>]
    ricloud --subscribe-device <account_id> <device_id> [--timeout=<timeout>]
    ricloud --unsubscribe-device <account_id> <device_id> [--timeout=<timeout>]
    ricloud --reset-subscription-since <account_id> <datetime> [--timeout=<timeout>]
    ricloud --help


Information:
    ricloud can be run in three modes:

    Listen mode:
        Starts a process which listends to feeds, system messages, and files being sent from asmaster, and saves these in the ricloud database.
        ricloud --listen [--timeout=<timeout>]

    Manager mode:
        To send messages to asmaster, such as to register a new account.
        The following actions are available with this mode:
            --list-services --list-subscriptions, --subscribe-account, --perform-2fa-challenge, --submit-2fa-challenge, --resubscribe-account, --unsubscribe-account, --list-devices, --subscribe-device, --unsubscribe-device

    Legacy interactive mode:
        For logging in to and downloading data from an account using with, without registering the account with asmaster (and without the corresponding locking prevention).
        ricloud <account> [--password=<password>] [--timeout=<timeout>]

    Debug mode:
        Check the status of running listeners using the debug commands: status.


Options:
    -h --help               Show this screen.
    --password=<password>   The password for this account.
    --timeout=<timeout>     How long should we wait for tasks to complete, in seconds. (default: 600s or 10 minutes)

"""
from __future__ import unicode_literals

import json
import logging
from docopt import docopt

from . import __version__
from .ricloud import RiCloud
from .asmaster_api import AsmasterApi
from .helpers import LogHelper
from .utils import select_service, select_samples


logger = logging.getLogger(__name__)


def _parse_input_arguments(arguments):
    timeout = int(arguments.get('--timeout') or 600)

    if arguments['status']:
        return {
            'mode': 'debug',
        }

    if arguments['--listen']:
        return {
            'mode': 'listen',
            'timeout': timeout,
        }

    manager_mode_actions = [
        'list-services',
        'list-subscriptions',
        'subscribe-account',
        'perform-2fa-challenge',
        'submit-2fa-challenge',
        'resubscribe-account',
        'unsubscribe-account',
        'list-devices',
        'subscribe-device',
        'unsubscribe-device',
        'reset-subscription-since',
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
    arguments = docopt(__doc__, version='ricloud v' + __version__)

    # Format the input arguments for the application
    application_payload = _parse_input_arguments(arguments)

    if application_payload['mode'] == 'interactive':
        logger.debug('Starting ricloud client in interactive mode.')
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
        logger.debug('Starting ricloud client in listener mode.')
        # asmaster listener requires MySQLdb, and we want to avoid requiring that otherwise
        from .asmaster_listener import AsmasterListener

        # This sets the listener running and will not return
        AsmasterListener(application_payload['timeout'])

    elif application_payload['mode'] == 'manager':
        logger.debug('Starting ricloud client manager request.')
        api = AsmasterApi(application_payload['timeout'])
        api.setup()

        if(arguments["--list-services"]):
            print json.dumps(api.list_services(), indent=2)
        if(arguments["--list-subscriptions"]):
            print json.dumps(api.list_subscriptions(arguments['<service>']), indent=2)
        if(arguments["--subscribe-account"]):
            print json.dumps(api.subscribe_account(
                arguments['<username>'],
                arguments['<password>'],
                arguments['<service>']), indent=2)
        if(arguments["--perform-2fa-challenge"]):
            print json.dumps(api.perform_2fa_challenge(arguments['<account_id>'], arguments['<device_id>']), indent=2)
        if(arguments["--submit-2fa-challenge"]):
            print json.dumps(api.submit_2fa_challenge(arguments['<account_id>'], arguments['<code>']), indent=2)
        if(arguments["--resubscribe-account"]):
            print json.dumps(api.resubscribe_account(arguments['<account_id>'], arguments['<password>']), indent=2)
        if(arguments["--unsubscribe-account"]):
            print json.dumps(api.unsubscribe_account(arguments['<account_id>']), indent=2)
        if(arguments["--list-devices"]):
            print json.dumps(api.list_devices(arguments['<account_id>']), indent=2)
        if(arguments["--subscribe-device"]):
            print json.dumps(api.subscribe_device(arguments['<account_id>'], arguments['<device_id>']), indent=2)
        if(arguments["--unsubscribe-device"]):
            print json.dumps(api.unsubscribe_device(arguments['<account_id>'], arguments['<device_id>']), indent=2)
        if(arguments["--reset-subscription-since"]):
            print json.dumps(api.reset_subscription_since(arguments['<account_id>'], arguments['<datetime>']), indent=2)

    elif application_payload['mode'] == 'debug':
        print json.dumps(LogHelper.get_status(), indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
