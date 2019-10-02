"""Sample implementations of various operations against the iCloud service."""
from __future__ import absolute_import

import click

import ricloud

from . import helpers
from .utils import info, warn, success, prompt, pause, await_response


def create_session(user_id, username, payload):
    info("Creating session...")

    source_attributes = {
        "user": user_id,
        "type": "icloud.account",
        "identifier": username,
    }

    session = ricloud.Session.create(source=source_attributes, payload=payload)

    await_response(session)

    if session.state == "failed":
        session = handle_session_creation_failure(session, username, payload)
    else:
        success("Session {} created.".format(session.id))

    return session


def handle_session_creation_failure(session, username, payload):
    if session.error == "code-required":
        info("Multi-factor authentication is on for this account.")
        payload["code"] = prompt("Please enter the received code")
        return create_session(session.user, username, payload)

    warn("Session initialisation failed with error: `{}`.".format(session.error))

    raise click.Abort


def parse_file_ids_from_result_data(result_data):
    file_ids = []
    for data_entry in result_data["data"]:
        if "files" in data_entry:
            # Just pick the first variant for many-file entries.
            file_ids.append(data_entry["files"][0]["id"])
        elif "file" in data_entry:
            file_ids.append(data_entry["file"]["id"])
    return file_ids


@click.command()
@click.argument("icloud_username")
@click.password_option(
    confirmation_prompt=False, help="The password of the iCloud account to access."
)
@click.option(
    "--user_identifier",
    "user_identifier",
    help="Optional. The `identifier` attribute of the User resource to associate this request with.",
)
@click.option(
    "--session",
    "session_id",
    help="Optional. The ID of the session to use for this request.",
)
def icloud(icloud_username, password, user_identifier=None, session_id=None):
    """Sample implementation for the iCloud service.

    Both ICLOUD_USERNAME and password are required.
    """
    user = helpers.get_or_create_user(user_identifier)

    if session_id:
        session = helpers.retrieve_session(session_id)
    else:
        session_payload = {"password": password}

        session = create_session(user.id, icloud_username, session_payload)

    data_type = prompt("Please enter a data type identifier", type=str)

    account_data_payload = {"data_types": [data_type]}

    poll = helpers.create_poll(account_data_payload, session=session)

    result_data = helpers.process_poll_results(poll)

    file_ids = parse_file_ids_from_result_data(result_data[data_type])

    if file_ids:
        info("Found {} files to download.".format(len(file_ids)))

        pause("Press any key to download the first 5 files...")

        account_files_payload = {"files": file_ids[:5]}

        poll = helpers.create_poll(payload=account_files_payload, session=session)

        helpers.process_poll_results(poll)
