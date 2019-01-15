"""Utilities for sample implementations."""
from __future__ import absolute_import

import time

import click


def info(message):
    click.secho(message, fg="yellow")


def warn(message):
    click.secho(message, fg="red")


def success(message):
    click.secho(message, fg="green")


def prompt(message, type=None):
    """Prompt the user for input."""
    return click.prompt(click.style(message, fg="blue"), type=type)


def pause(message):
    """Block until the user presses 'any key'."""
    click.pause(info=click.style(message, fg="blue"))


def await_response(resource, timeout=60):
    """Poll the API until processing resolves or the timeout is reached."""
    timeout_time = time.time() + timeout
    while resource.state in ("pending", "processing") and time.time() < timeout_time:

        time.sleep(1)

        resource.refresh()
