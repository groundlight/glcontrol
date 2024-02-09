#!/usr/bin/env -S poetry run python
import os
import time

import typer
from framegrab.cli.clitools import preview_image

from glcontrol.cfgtools.specs import GLControlManifest
from glcontrol.runner import SpecRunner

app = typer.Typer()


def set_default_config_fn(config_fn: str) -> str:
    """If the config file is not specified, look for a default.
    If no default available, raise an error."""
    if config_fn:
        return config_fn
    if "GLCONTROL_CONFIG" in os.environ:
        return os.environ["GLCONTROL_CONFIG"]
    raise ValueError("No config file specified and no default found in environment GLCONTROL_CONFIG.")


def display_config_if_updated(config_fn: str, last_updated: float) -> float:
    """Checks if the config file has been updated and if so, prints the new config."""
    config_fn = set_default_config_fn(config_fn)
    # check if the file exists
    if not os.path.exists(config_fn):
        print(f"File not found: {config_fn}")
        return last_updated

    # check if the file has been updated
    if last_updated != os.path.getmtime(config_fn):
        print(f"Runtime config file: {config_fn}")
        # Just print out the raw yaml for now
        with open(config_fn, "r") as f:
            print(f.read())
        print(f"<end> of {config_fn}")

    return os.path.getmtime(config_fn)


@app.command()
def watch_config(config: str = "", poll_delay: float = 1.0):
    """Watches the runtime config file and prints it to the console when it changes.
    This is useful as a dev tool to see the config changes in real time.
    """
    config_fn = set_default_config_fn(config)
    last_updated = 0  # set to 0 to force initial display
    while True:
        last_updated = display_config_if_updated(config_fn, last_updated=last_updated)
        time.sleep(poll_delay)


@app.command()
def start(config: str = ""):
    """Starts the Groundlight runtime.
    Parses the config YAML and launches all the control loops."""
    config_fn = set_default_config_fn(config)
    raise NotImplementedError("Not yet implemented.")


@app.command()
def stop():
    """Stops the Groundlight runtime.
    Stops all the control loops."""
    raise NotImplementedError("Not yet implemented.")


@app.command()
def parse(config_fn: str = typer.Argument(...)):
    """Parses the config YAML and says if it's valid or not."""
    manifest = GLControlManifest.from_file(config_fn)
    assert manifest
    print(f"Config file {config_fn} is valid.")


@app.command()
def preview_cameras(config_fn: str = typer.Argument(...)):
    """Instantiates the cameras and shows a preview of each one."""
    manifest = GLControlManifest.from_file(config_fn)
    runner = SpecRunner(manifest.glcontrol)
    for n, grabber in enumerate(runner._grabbers):
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
