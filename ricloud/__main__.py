"""ricloud API Client.

Usage:
    ricloud <account> [--password=<password>] [--timeout=<timeout>]

Options:
    -h --help               Show this screen.
    --password=<password>   The password for this account.
    --timeout=<timeout>     How long should we wait for tasks to complete, in seconds. (default: 600s or 10 minutes)

"""
from __future__ import unicode_literals

from docopt import docopt

from .ricloud import RiCloud
from .conf import DEFAULT_LOG
from .utils import LogFile, select_service, select_samples


def _parse_input_arguments(arguments):
    account = arguments['<account>']
    password = arguments.get('--password', None)
    timeout = int(arguments.get('--timeout') or 600)

    return {
        'account': account,
        'password': password,
        'timeout': timeout
    }


def main():
    # Get input arguments from command line
    arguments = docopt(__doc__)

    # Format the input arguments for the application
    application_payload = _parse_input_arguments(arguments)

    # Main RiCloud object
    ricloud = RiCloud(log=LogFile(DEFAULT_LOG))

    # The RiCloud client retrieves a list of available services from the API.
    service_name = select_service(ricloud)

    # Each service has a client which contains all the available tasks.
    # Sample applications for these clients can be found in the `samples` folder.
    Application = select_samples(ricloud, service_name, application_payload)

    # Execute the application's main function.
    Application.run()


if __name__ == '__main__':
    main()
