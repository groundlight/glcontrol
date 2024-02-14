#!/usr/bin/env -S poetry run python
import os
import time

import typer
from framegrab.cli.clitools import preview_image

from glcontrol.cfgtools.specs import GLControlManifest
from glcontrol.runner import SpecRunner

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def set_default_config_path(config_path: str) -> str:
    """If the config file is not specified, look for a default.
    If no default available, raise an error."""
    if config_path:
        return config_path
    if "GLCONTROL_CONFIG" in os.environ:
        return os.environ["GLCONTROL_CONFIG"]
    raise ValueError("No config file specified and no default found in environment GLCONTROL_CONFIG.")


def display_config_if_updated(config_path: str, last_updated: float) -> float:
    """Checks if the config file has been updated and if so, prints the new config."""
    config_path = set_default_config_path(config_path)
    # check if the file exists
    if not os.path.exists(config_path):
        print(f"File not found: {config_path}")
        return last_updated

    # check if the file has been updated
    if last_updated != os.path.getmtime(config_path):
        print(f"Runtime config file: {config_path}")
        # Just print out the raw yaml for now
        with open(config_path, "r") as f:
            print(f.read())
        print(f"<end> of {config_path}")

    return os.path.getmtime(config_path)


@app.command()
def watch_config(config: str = "", poll_delay: float = 1.0):
    """Watches the runtime config file and prints it to the console when it changes.
    This is useful as a dev tool to see the config changes in real time.
    """
    config_path = set_default_config_path(config)
    last_updated = 0  # set to 0 to force initial display
    while True:
        last_updated = display_config_if_updated(config_path, last_updated=last_updated)
        time.sleep(poll_delay)


@app.command()
def start(config: str = ""):
    """Starts the Groundlight runtime.
    Parses the config YAML and launches all the control loops."""
    config_path = set_default_config_path(config)
    raise NotImplementedError(f"Not yet implemented {config_path}")


@app.command()
def stop():
    """Stops the Groundlight runtime.
    Stops all the control loops."""
    raise NotImplementedError("Not yet implemented.")


@app.command()
def parse(config_path: str = typer.Argument(...)):
    """Parses the config YAML and says if it's valid or not."""
    manifest = GLControlManifest.from_file(config_path)
    assert manifest
    print(f"Config file {config_path} is valid.")


@app.command()
def preview_cameras(config_path: str = typer.Argument(...)):
    """Instantiates the cameras and shows a preview of each one."""
    manifest = GLControlManifest.from_file(config_path)
    runner = SpecRunner(manifest.glcontrol)
    for n, grabber in enumerate(runner.grabbers):
        frame = grabber.grab()
        preview_image(frame, title=f"camera {n}", output_type="imgcat")


@app.command()
def restart():
    """Restarts the Groundlight runtime.
    Stops all the control loops and then starts them again."""
    raise NotImplementedError("Not yet implemented.")


def climain():
    app()


if __name__ == "__main__":
    climain()
