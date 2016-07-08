import getpass
import json
import os

from ricloud.api import RiCloud
from ricloud.exceptions import TwoFactorAuthenticationRequired

try:
    from unidecode import unidecode
except:
    print "\n\n** Print please install unidecode: pip install unidecode **\n\n"
    raise


def choose_device(devices):
    print "\nYour devices:"
    device_ids = []
    for index, id in enumerate(devices):
        device_ids.append(id)
        name = devices[id]["device_name"]
        model = devices[id]["model"]
        colour = devices[id]["colour"]
        latest = devices[id]["latest-backup"]

        print "%s - %s [model: %s, colour: %s, latest-backup: %s]" % (index, unidecode(name), model, colour, latest)

    print "\nChoose a device by specifying its index (e.g. 0):",
    return device_ids[input()]


def choose_trusted_device(trusted_devices):
    print '\n2FA has been enabled, choose a trusted device:'
    for index, device in enumerate(trusted_devices):
        print "%s - %s" % (index, device)
    print "\nChoose a device by specifying its index (e.g. 0):",
    return trusted_devices[input()]


def get_2fa_code():
    print '\nA code has been sent to your device.'
    print 'Code: ',
    return raw_input()


def get_login():
    email = raw_input("Please enter your Apple ID: ")
    password = getpass.getpass("Please enter your password: ")
    return email, password


def get_data_mask():
    print '\nWhat would you like to download?\n'
    for mask, display_name in RiCloud._backup_client_class.AVAILABLE_DATA:
        print str(mask).ljust(7), display_name

    print '\nMask (0) for all: ',
    return input()


def main():
    email, password = get_login()
    api = RiCloud()

    try:
        api.login(email, password)
    except TwoFactorAuthenticationRequired:
        trusted_device = choose_trusted_device(api.trusted_devices)
        api.request_2fa_challenge(challenge_device=trusted_device)
        code = get_2fa_code()
        api.submit_2fa_challenge(code=code)
        api.login(email, password)

    device_id = choose_device(api.devices)

    mask = get_data_mask()
    data = api.backup_client.request_data(device_id=device_id, data_mask=mask)

    # Let's setup the output
    try:
        os.mkdir('out')
    except OSError:
        # Dir already exists (most likely)
        pass

    with open(os.path.join('out', 'data.json'), 'wb') as out:
        json.dump(data, out, indent=4)

    if 'photos' in data and isinstance(data['photos'], list):
        for photo in data['photos']:
            # It can get the "Contact enterprise" message, in which case we cannot access `filename`
            if 'filename' in photo:
                with open(os.path.join('out', photo['filename']), 'wb') as out:
                    api.backup_client.download_file(device_id,
                                                    photo['file_id'], out)

    print 'Complete! All data is in the directory "out".'

if __name__ == '__main__':
    main()
