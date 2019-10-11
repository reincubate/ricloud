"""Sample implementation of operations against the Rirelay service."""
from __future__ import absolute_import

import click

import ricloud
from ricloud import compat

from . import helpers
from .utils import success, info, warn, await_response


def create_session(user_id, rirelay_pairing_code):
    info("Creating session...")

    source_attributes = {"user": user_id, "type": "rirelay.instance"}

    payload = {"code": rirelay_pairing_code}

    session = ricloud.Session.create(source=source_attributes, payload=payload)

    await_response(session)

    if session.state == "failed":
        session = handle_session_creation_failure(session, rirelay_pairing_code)
    else:
        success("Session created, ID: {}".format(session.id))

    return session


def handle_session_creation_failure(session, rirelay_pairing_code):
    if session.error == "code-invalid":
        warn(
            "The pairing code was not recognised by the Rirelay service. Please check it and try again."
        )
    else:
        warn("Session initialisation failed with error: `{}`.".format(session.error))

    raise click.Abort


@click.group()
def rirelay():
    """Sample implementation for the rirelay service."""
    pass


@rirelay.group(name="session")
def rirelay_session():
    """Commands to interact with rirelay sessions."""
    pass


@rirelay_session.command(name="create")
@click.argument("rirelay_pairing_code")
@click.option(
    "--user-identifier",
    "user_identifier",
    help="Optional. The `identifier` attribute of the User resource to associate this request with.",
)
def cmd_session_create(rirelay_pairing_code, user_identifier=None):
    user = helpers.get_or_create_user(user_identifier)

    session = create_session(user.id, rirelay_pairing_code)

    info(compat.to_str(session))


@rirelay_session.command(name="retrieve")
@click.argument("session_id")
def cmd_session_retrieve(session_id):
    session = helpers.retrieve_session(session_id)

    info(compat.to_str(session))


@rirelay.group(name="sub")
def rirelay_sub():
    """Commands to interact with rirelay subscriptions."""
    pass


@rirelay_sub.command(name="create")
@click.argument("session_id")
@click.argument("source_id")
@click.option("--info-types", type=str, help="The info types to be polled.")
@click.option("--data-types", type=str, help="The data types to be polled.")
@click.option("--files", type=str, help="The files to be polled for.")
def cmd_sub_create(session_id, source_id, info_types, data_types, files):
    session = helpers.retrieve_session(session_id)

    poll_payload = helpers.build_poll_payload(info_types, data_types, files)

    sub = helpers.create_subscription(
        session, source=source_id, poll_payload=poll_payload
    )

    info(compat.to_str(sub))


@rirelay_sub.command(name="retrieve")
@click.argument("subscription_id")
def cmd_sub_retrieve(subscription_id):
    sub = ricloud.Subscription.retrieve(id=subscription_id)

    info(compat.to_str(sub))


@rirelay_sub.command(name="poll")
@click.argument("subscription_id")
@click.option("--info-types", type=str, help="The info types to be polled.")
@click.option("--data-types", type=str, help="The data types to be polled.")
@click.option("--files", type=str, help="The files to be polled for.")
def cmd_sub_poll(subscription_id, info_types, data_types, files):
    """Create a manual poll against an existing subscription."""
    payload = helpers.build_poll_payload(info_types, data_types, files)

    poll = helpers.create_poll(payload, subscription=subscription_id)

    info(compat.to_str(poll))


@rirelay_sub.command(name="latest")
@click.argument("subscription_id")
def cmd_sub_latest(subscription_id):
    """Retrieve the latest automatic poll for the subscription."""
    polls = ricloud.Poll.list(
        subscription=subscription_id, requestor="subscription", limit=1
    )

    if not polls:
        info("No automatic polls found for this subscription.")
        return

    poll = polls[0]

    info(compat.to_str(poll))
