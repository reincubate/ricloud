from __future__ import absolute_import, print_function

from flask import Flask, request, abort

from ricloud import conf
from ricloud.signing import Signature
from ricloud.utils import decode_json, encode_json


app = Flask(__name__)


RICLOUD_EVENTS_SECRET = conf.get("events", "secret")
RICLOUD_EVENTS_DELTA = conf.getint("events", "delta")


@app.route("/events/<uuid:event_id>", methods=["post"])
def events(event_id):
    if not request.json:
        abort(400)

    webhook_secret = app.config.get("WEBHOOK_SECRET", RICLOUD_EVENTS_SECRET)

    if webhook_secret and not verify_request(request, webhook_secret):
        abort(400)

    data = decode_json(request.json)

    only = app.config.get("EVENTS_ONLY")
    exclude = app.config.get("EVENTS_EXCLUDE")

    try:
        handle_event(data, only=only, exclude=exclude)
    except Exception as exc:
        print("Exception occurred during event handling:", str(exc))
        abort(400)

    return "OK"


def verify_request(request, secret, delta=RICLOUD_EVENTS_DELTA):
    signature = Signature.from_header(request.headers.get("Ricloud-Signature"))

    try:
        signature.verify(request.json, secret, delta=delta)
    except Signature.SignatureError as exc:
        print("Event signature verification failed:", str(exc))
        return False

    return True


def handle_event(data, only=None, exclude=None):
    event_type = data["type"]
    event_action = data["action"]
    event_slug = event_type + "." + event_action

    if only and event_slug not in only:
        return

    if exclude and event_slug in exclude:
        return

    print("Event received:", encode_json(data, indent=2))
