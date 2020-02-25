from __future__ import absolute_import

from click.testing import CliRunner

from ricloud.cli import cli


class TestHelp(object):
    def test_ok(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
