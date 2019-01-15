"""Sample implementations of various operations against the iCloud service."""
from __future__ import absolute_import

import click

import ricloud
from ricloud import conf
from ricloud import storage
from ricloud import utils

from .utils import info, warn, success, prompt, pause, await_response


def get_or_create_user(user_identifier):
    info("Getting user...")

    user_identifier = user_identifier or conf.get('samples', 'user_identifier')

    user = ricloud.User.create(identifier=user_identifier)

    success("User {} retrieved.".format(user.id))
    return user


def create_session(user_id, username, payload):
    info("Creating session...")

    source_attributes = {
        "user": user_id,
        "type": "icloud.account",
        "identifier": username
    }

    session = ricloud.Session.create(
        source=source_attributes,
        payload=payload,
    )

    await_response(session)

    if session.state == "failed":
        session = handle_session_creation_failure(session, username, payload)
    else:
        success("Session {} created.".format(session.id))

    return session


def retrieve_session(session_id):
    info("Retrieving session {}...".format(session_id))

    session = ricloud.Session.retrieve(session_id)

    success("Session {} retrieved.".format(session_id))
    return session


def handle_session_creation_failure(session, username, payload):
    if session.error == "code-required":
        info("Multi-factor authentication is on for this account.")
        payload["code"] = prompt("Please enter the received code")
        return create_session(session.user, username, payload)

    warn("Session initialisation failed with error: `{}`.".format(session.error))

    raise click.Abort


def await_poll(poll):
    info("Awaiting poll completion...")

    await_response(poll)

    if poll.state == "failed":
        warn("Poll failed with error: `{}`".format(poll.error))
        raise click.Abort
    else:
        success("Poll {} completed.".format(poll.id))


def create_poll(session, type, payload=None, source=None):
    info("Creating account {} poll...".format(type))

    request_payload = {"session": session, "type": type}

    if payload:
        request_payload["payload"] = payload

    if source:
        request_payload["source"] = source

    poll = ricloud.Poll.create(**request_payload)

    await_poll(poll)

    return poll


def process_poll_results(poll):
    success("Processing results:")
    results = {}
    for result in poll.results:
        identifier = result["identifier"]

        success(" - identifier {}".format(identifier))
        success("   stored at {}".format(result["url"]))

        filename = utils.escape(identifier)
        filename = utils.get_filename(poll.id, filename)

        storage.download_result(result["url"], to_filename=filename)

        if result["type"] == "json":
            with open(filename, "rb") as f:
                raw_result_data = f.read()
            result_data = utils.decode_json(raw_result_data)
            results[identifier] = result_data
        else:
            results[identifier] = filename

        success("   downloaded locally to {}".format(filename))
    return results


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
@click.argument(
    "icloud_username"
)
@click.password_option(
    confirmation_prompt=False, help='The password of the iCloud account to access.'
)
@click.option(
    "--user_identifier",
    "user_identifier",
    help='Optional. The `identifier` attribute of the User resource to associate this request with.'
)
@click.option(
    "--session",
    "session_id",
    help='Optional. The ID of the session to use for this request.'
)
def icloud(icloud_username, password, user_identifier=None, session_id=None):
    """Sample implementation of the iCloud login and data retrieval process.

    Both ICLOUD_USERNAME and password are required.
    """
    user = get_or_create_user(user_identifier)

    if session_id:
        session = retrieve_session(session_id)
    else:
        session_payload = {"password": password}

        session = create_session(user.id, icloud_username, session_payload)

    data_type = prompt("Please enter a data type identifier", type=str)

    account_data_payload = {"data_types": [data_type]}

    poll = create_poll(session, "data", account_data_payload)

    result_data = process_poll_results(poll)

    file_ids = parse_file_ids_from_result_data(result_data[data_type])

    if file_ids:
        info("Found {} files to download.".format(len(file_ids)))

        pause("Press any key to download the first 5 files...")

        account_files_payload = {"file_ids": file_ids[:5]}

        poll = create_poll(session, "files", account_files_payload)

        process_poll_results(poll)
