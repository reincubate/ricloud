from __future__ import absolute_import

import click

import ricloud
from ricloud import conf
from ricloud import storage
from ricloud import utils

from .utils import info, warn, success, await_response


def get_or_create_user(user_identifier):
    info("Getting user...")

    user_identifier = user_identifier or conf.get("samples", "user_identifier")

    user = ricloud.User.create(identifier=user_identifier)

    success("User {} retrieved.".format(user.id))
    return user


def retrieve_session(session_id):
    info("Retrieving session {} ...".format(session_id))

    session = ricloud.Session.retrieve(session_id)

    success("Session {} retrieved.".format(session_id))
    return session


def create_subscription(session, poll_payload, source=None):
    info("Creating subscription...")

    request_payload = {"session": session, "poll_payload": poll_payload}

    if source:
        request_payload["source"] = source

    sub = ricloud.Subscription.create(**request_payload)

    await_response(sub)

    if session.state == "pending":
        warn(
            "Subscription created but not allowed by the app instance within the timeout."
        )
    else:
        success("Subscription created, ID: {}".format(sub.id))

    return sub


def build_poll_payload(info_types, data_types, files):
    payload = {}

    if not (info_types or data_types or files):
        payload["data_types"] = ["ios_messages.messages"]

    if info_types:
        payload["info_types"] = info_types.split(",")

    if data_types:
        payload["data_types"] = data_types.split(",")

    if files:
        payload["files"] = files.split(",")

    return payload


def await_poll(poll):
    info("Awaiting completion of poll {} ...".format(poll.id))

    await_response(poll)

    if poll.state == "failed":
        warn("Poll failed with error: `{}`".format(poll.error))
        raise click.Abort
    else:
        success("Poll {} completed.".format(poll.id))


def create_poll(payload, session=None, source=None, subscription=None):
    info("Creating poll...")

    request_payload = {"payload": payload}

    if session:
        request_payload["session"] = session

    if source:
        request_payload["source"] = source

    if subscription:
        request_payload["subscription"] = subscription

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
