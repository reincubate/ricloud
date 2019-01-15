from __future__ import absolute_import, print_function

import click
import ricloud
import ricloud.samples


@click.group()
def cli():
    pass


@cli.group()
def webhook_config():
    pass


@webhook_config.command()
@click.option("--url", help="The webhook config url attribute.")
def create(url):
    webhook_config = ricloud.WebhookConfig.create(url=url)

    print(webhook_config)


@webhook_config.command()
@click.argument("id")
def test(id):
    webhook_config_test_task = ricloud.WebhookConfig(id=id).test()

    print(webhook_config_test_task)


@cli.group()
def storage_config():
    pass


@storage_config.command()
@click.option("--url", help="The storage config url attribute.")
@click.option("--credentials-path", "credentials_path", type=click.Path(exists=True))
def create(url, credentials_path):
    credentials = ricloud.StorageConfig.read_credentials_file(credentials_path)

    storage_config = ricloud.StorageConfig.create(url=url, credentials=credentials)

    print(storage_config)


@storage_config.command()
@click.argument("id")
def test(id):
    storage_config_test_task = ricloud.StorageConfig(id=id).test()

    print(storage_config_test_task)


@cli.group()
def samples():
    pass


samples.add_command(ricloud.samples.icloud)
