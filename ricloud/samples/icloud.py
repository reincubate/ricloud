from __future__ import absolute_import

import click

import ricloud
from ricloud import compat

from . import helpers
from .utils import success, info, warn, prompt, await_response


def create_session(user_id, icloud_username, icloud_password, icloud_mfa_code=None):
    info("Creating session for {}...".format(icloud_username))

    source_attrs = {
        "user": user_id,
        "type": "icloud.account",
        "identifier": icloud_username,
    }

    payload = {
        "password": icloud_password,
    }

    if icloud_mfa_code:
        payload["code"] = icloud_mfa_code

    session = ricloud.Session.create(source=source_attrs, payload=payload)

    await_response(session)

    if session.state == "failed":
        session = handle_session_creation_failure(session, icloud_username, icloud_password, icloud_mfa_code)
    elif session.state == "pending":
        warn((
            "Session {session_id} could not be initialised within client timeout.\n"
            "Please retrieve it to check initialisation status:\n"
            "\tricloud icloud session retrieve {session_id}"
        ).format(
            session_id=session.id
        ))
        raise click.Abort

    success("Session created: {}".format(session.id))

    return session


def handle_session_creation_failure(session, icloud_username, icloud_password, icloud_mfa_code):
    if session.error == "code-required":
        if not icloud_mfa_code:
            info("Multi-factor authentication is on for this account.")
        else:
            warn("Invalid code provided. Retrying...")

        code = prompt("Please enter the received code")

        return create_session(session.user, icloud_username, icloud_password, icloud_mfa_code=code)

    warn("Session initialisation failed with error: `{}`.".format(session.error))

    raise click.Abort


@click.group()
def icloud():
    pass


@icloud.group(name="session")
def icloud_session():
    pass


@icloud_session.command(name="create")
@click.argument("icloud_username")
@click.password_option("--icloud-password",
    confirmation_prompt=False, help="The password of the iCloud account to access."
)
@click.option("--user-identifier", "user_identifier", help="Optional. The `identifier` attribute of the User resource to associate this request with.",)
def cmd_session_create(icloud_username, icloud_password, user_identifier=None):
    user = helpers.get_or_create_user(user_identifier)

    session = create_session(user.id, icloud_username, icloud_password)

    info(compat.to_str(session))


@icloud_session.command(name="retrieve")
@click.argument("session_id")
def cmd_session_retrieve(session_id):
    session = helpers.retrieve_session(session_id)

    info(compat.to_str(session))


@icloud_session.command(name="latest")
@click.argument("source_identifier")
@click.option("--user-identifier", "user_identifier", help="Optional. The `identifier` attribute of the User resource to associate this request with.",)
def cmd_session_latest(source_identifier, user_identifier=None):
    user = helpers.get_or_create_user(user_identifier)

    sources = ricloud.Source.list(
        user=user,
        identifier=source_identifier
    )

    if sources.data:
        source = sources.data[0]
    else:
        warn("No sources (identifier:{src_identifier}) found for user (identifier:{usr.identifier}).".format(
            src_identifier=source_identifier, usr=user
        ))
        raise click.Abort

    sessions = ricloud.Session.list(
        source=source,
        state='active',
        limit=1
    )

    if sessions.data:
        session = sessions.data[0]
    else:
        warn("No active sessions exist for source (id:{src.id}, identifier:{src.identifier}).".format(src=source))
        raise click.Abort

    info(compat.to_str(session))


@icloud.group(name="poll")
def icloud_poll():
    pass


@icloud_poll.command(name="create")
@click.argument("session_id")
@click.option("--source-id", type=str, help="The source to target, if different from the session's primary source.")
@click.option("--info-types", type=str, help="The info types to be polled.")
@click.option("--data-types", type=str, help="The data types to be polled.")
@click.option("--files", type=str, help="The files to be polled for.")
def cmd_poll_create(session_id, source_id, info_types, data_types, files):
    payload = helpers.build_poll_payload(info_types, data_types, files)

    poll = helpers.create_poll(payload, session=session_id, source=source_id)

    info(compat.to_str(poll))


@icloud_poll.command(name="retrieve")
@click.argument("poll_id")
def cmd_poll_retrieve(poll_id):
    poll = ricloud.Poll.retrieve(id=poll_id)

    info(compat.to_str(poll))


@icloud_poll.command(name="latest")
@click.argument("session_id")
def cmd_poll_latest(session_id):
    polls = ricloud.Poll.list(session=session_id, limit=1)

    if polls.data:
        poll = polls.data[0]
    else:
        warn("No polls found for session (id:{})".format(session_id))
        raise click.Abort

    info(compat.to_str(poll))


@icloud_poll.command(name="download")
@click.argument("poll_id")
@click.option("--only", type=str, help="Only download results with particular identifiers. Can be a single identifier or comma-separated list of identifiers.")
@click.option("--cascade", type=bool, default=True, help="Create an additional poll to retrieve files found in the initial poll's results.")
@click.option("--limit", type=int, default=5, help="Only download the first n files from each result data type.")
def cmd_poll_download(poll_id, only, cascade, limit):
    """"Download results created from a data poll."""
    poll = ricloud.Poll.retrieve(id=poll_id)

    data, files = helpers.process_poll_results(poll, only=only, cascade=cascade, limit=limit)


@icloud.group(name="result")
def icloud_result():
    pass


@icloud_result.command(name="retrieve")
@click.argument("result_id")
def cmd_result_retrieve(result_id):
    result = ricloud.Result.retrieve(id=result_id)

    info(compat.to_str(result))


@icloud_result.command(name="download")
@click.argument("result_id")
def cmd_result_download(result_id):
    result = ricloud.Result.retrieve(id=result_id)

    helpers.download_result(result)
