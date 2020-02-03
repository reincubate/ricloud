from __future__ import absolute_import, print_function

from flask import Flask, request, abort

from ricloud.signing import Signature
from ricloud.utils import encode_json


app = Flask(__name__)


@app.route("/webhooks/<uuid:event_id>", methods=["post"])
def webhooks(event_id):
    if not request.is_json:
        abort(400)

    webhook_secret = app.config.get("WEBHOOK_SECRET")
    webhook_delta = app.config.get("WEBHOOK_DELTA")

    if webhook_secret and not verify_request(
        request, webhook_secret, delta=webhook_delta
    ):
        abort(400)

    only = app.config.get("EVENTS_ONLY")
    exclude = app.config.get("EVENTS_EXCLUDE")

    try:
        handle_event(request.json, only=only, exclude=exclude)
    except Exception as exc:
        print("Exception occurred during event handling:", str(exc))
        abort(400)

    return "OK"


def verify_request(request, secret, delta=600):
    signature = Signature.from_header(request.headers["Ricloud-Signature"])

    try:
        signature.verify(request.data, secret, delta=delta)
    except Signature.SignatureError as exc:
        print("Event signature verification failed:", str(exc))
        return False

    return True


def handle_event(data, only=None, exclude=None):
    event_type = data["type"]
    event_action = data["action"]
    event_slug = event_type + "." + event_action

    if event_slug == "webhook_config.test":
        print("Test event received!")

    if only and event_slug not in only:
        return

    if exclude and event_slug in exclude:
        return

    print("Event received:", encode_json(data, indent=2))
