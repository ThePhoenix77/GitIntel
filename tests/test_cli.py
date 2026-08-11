from typer.testing import CliRunner

from gitintel import __version__
from gitintel.cli import app

runner = CliRunner()


def test_version_option():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"{__version__}\n"


def test_module_help():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Analyze a Git repository." in result.stdout
