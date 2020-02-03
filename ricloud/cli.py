from __future__ import absolute_import, print_function

import os

import click
import ricloud
import ricloud.samples
from ricloud import utils


@click.group()
def cli():
    pass


@cli.group("config")
def config():
    """Local ricloud configuration commands."""
    pass


@config.command("init")
@click.option("--token", prompt=True, help="The key token to use.")
@click.option("--url", help="The API endpoint URL to use.")
def init(token, url=None):
    """Helper to initialise the ricloud client's local configuration."""
    from ricloud import conf

    conf_path = conf.get_user_root_config_path()

    if os.path.exists(conf_path):
        click.secho(
            "ricloud configuration already exists at: {}".format(conf_path), fg="red"
        )
        raise click.Abort

    settings = conf.settings
    settings.set("api", "token", token)

    if url:
        settings.set("api", "url", url)

    with open(conf_path, "w") as conf_file:
        settings.write(conf_file)

    click.secho("ricloud configuration created at: {}".format(conf_path), fg="green")


@config.command("view")
def view():
    """Prints the contents of the ricloud client's local configuration."""
    from ricloud import conf

    settings = conf.settings
    for section in settings.sections():
        click.echo("[{}]".format(section))
        for name, value in settings.items(section):
            click.echo("{} = {}".format(name, value))
        click.echo()  # Separate sections by newline.


@cli.group()
def webhook_config():
    """Helpers to create and test webhook configs."""
    pass


@webhook_config.command("create")
@click.option("--url", help="The webhook config url attribute.")
def webhook_config_create(url):
    """Create a webhook config."""
    webhook_config = ricloud.WebhookConfig.create(url=url)

    click.echo(webhook_config)


@webhook_config.command("test")
@click.argument("id")
def webhook_config_test(id):
    """Test a webhook config."""
    webhook_config_test_task = ricloud.WebhookConfig(id=id).test()

    click.echo(webhook_config_test_task)


@cli.group()
def storage_config():
    """Helpers to create and test storage configs."""
    pass


@storage_config.command("create")
@click.option("--url", help="The storage config url attribute.")
@click.option("--credentials-path", "credentials_path", type=click.Path(exists=True))
def storage_config_create(url, credentials_path):
    """Create a storage config."""
    credentials = ricloud.StorageConfig.read_credentials_file(credentials_path)

    storage_config = ricloud.StorageConfig.create(url=url, credentials=credentials)

    print(storage_config)


@storage_config.command("test")
@click.argument("id")
def storage_config_test(id):
    """Test a storage config."""
    storage_config_test_task = ricloud.StorageConfig(id=id).test()

    click.echo(storage_config_test_task)


@cli.group()
def samples():
    pass


samples.add_command(ricloud.samples.icloud)
cli.add_command(ricloud.samples.icloud)
samples.add_command(ricloud.samples.rirelay)
cli.add_command(ricloud.samples.rirelay)


@cli.group()
def event():
    """Helpers to consume ricloud API event notifications."""
    pass


@event.command()
@click.argument("host", default="0.0.0.0")
@click.argument("port", default="8080")
@click.option("--debug", is_flag=True, help="Controls the Flask debug setting.")
@click.option(
    "--webhook-url",
    default=None,
    help="Automatically sets up a webhook config for this URL.",
)
@click.option(
    "--only",
    default=None,
    help="Comma separated list. Only echo events with these slugs.",
)
@click.option(
    "--exclude",
    default=None,
    help="Comma separated list. Exclude events with these slugs.",
)
def listen(host, port, debug, webhook_url, only, exclude):
    """ricloud API event notification listener.

    Sets up a small Flask-based server listening on HOST (default: 0.0.0.0) and PORT (default: 8080).

    It is likely that you are using something like ngrok to expose the endpoint to the API. If that's the case, pass in the forwarding URL using the --webhook-url option. This will automatically setup a webhook config on the API and set it as active for your key (assuming it is valid).

    In most cases, you will likely set up a utility like ngrok to expose this endpoint to the internet.

    The default handler simply echos received event data to stdout.
    """
    from ricloud import conf

    webhook_secret = conf.get("webhooks", "secret")
    webhook_delta = conf.getint("webhooks", "delta")

    if webhook_url:
        key = ricloud.Key.current()

        url = utils.join_url(webhook_url, "webhooks")
        webhook_config = ricloud.WebhookConfig.create(url=url)

        if key.webhook_config != webhook_config.id:
            key.update(webhook_config=webhook_config)

        message = "Using webhook config with ID {}".format(webhook_config.id)
        click.secho(message, fg="yellow")

        webhook_secret = webhook_config.secret

    from ricloud.webhooks import app

    app.config["WEBHOOK_SECRET"] = webhook_secret
    app.config["WEBHOOK_DELTA"] = webhook_delta
    app.config["EVENTS_ONLY"] = only
    app.config["EVENTS_EXCLUDE"] = exclude

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        webhook_config.delete()
