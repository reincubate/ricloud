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
    elif poll.state == "pending":
        warn((
            "Poll {poll_id} did not to complete within client timeout. "
            "Please retrieve it using: ricloud icloud poll retrieve {poll_id}"
        ).format(poll_id=poll["id"]))
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


def process_poll_results(poll, only=None, cascade=False, limit=None):
    info("Downloading results...")

    if only:
        results = [result for result in poll.results if result["identifier"] in only]
    else:
        results = poll.results

    return download_results(results, cascade=cascade, limit=limit, poll=poll)


def download_results(results, cascade=False, limit=None, poll=None):
    result_data = {}
    files = {}
    
    for result in results:
        download, is_json = download_result(result, poll=poll)
        import pdb; pdb.set_trace()
        if is_json:
            result_data[result["identifier"]] = download
        else:
            files[result["identifier"]] = download

        if is_json and cascade:
            file_ids = parse_file_ids_from_result_data(download)

            if limit:
                file_ids = file_ids[:limit]

            payload = {"files": file_ids}

            cascade_poll = create_poll(payload, session=poll["session"], source=poll["source"])

            _, cascade_files = download_results(cascade_poll.results, poll=poll)

            files.update(cascade_files)

    return result_data, files


def download_result(result, to_filename=None, poll=None):
    success("Downloading result {}:".format(result["id"]))
    success(" - identifier {}".format(result["identifier"]))
    success(" - stored at {}".format(result["url"]))

    if not to_filename:
        to_filename = utils.escape(result["identifier"])
        poll_id = poll["id"] if poll else result["poll"]
        to_filename = utils.get_filename(poll_id, to_filename)

    storage.download_result(result["url"], to_filename=to_filename)

    is_json = (result["type"] == "json")

    if is_json:
        with open(to_filename, "rb") as f:
            raw_result_data = f.read()
        result_data = utils.decode_json(raw_result_data)
        download =  result_data
    else:
        download = to_filename

    success(" - downloaded to {}".format(to_filename))
    return download, is_json


def parse_file_ids_from_result_data(result_data):
    file_ids = []
    for data_entry in result_data["data"]:
        if "files" in data_entry:
            # Just pick the first variant for many-file entries.
            file_ids.append(data_entry["files"][0]["id"])
        elif "file" in data_entry:
            file_ids.append(data_entry["file"]["id"])
        elif "attachments" in data_entry:
            ids = [f["file_id"] for f in data_entry["attachments"] if "dtouch" not in f["file_id"]]
            file_ids.extend(ids)
    return file_ids
