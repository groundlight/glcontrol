from typer.testing import CliRunner

from glcontrol.cli import app


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    print(result.output)

def test_cli_noargs():
    """Test that the cli main function runs without error."""
    runner = CliRunner()
    result = runner.invoke(app, [])  # Simulating no arguments passed
    assert result.exit_code != 0  # Non-zero exit code indicates an error

