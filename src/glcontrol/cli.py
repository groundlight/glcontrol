#!/usr/bin/env -S poetry run python
import os
import time

import typer

import glcontrol.conductor as conductor

RUNTIME_CONFIG_FN = "/opt/groundlight/config/runtime.yaml"


app = typer.Typer()


def display_config_if_updated(config_fn: str, last_updated: float) -> float:
    """Checks if the config file has been updated and if so, prints the new config.
    """
    # check if the file exists
    if not os.path.exists(config_fn):
        print(f"File not found: {config_fn}")
        return last_updated

    # check if the file has been updated
    if last_updated != os.path.getmtime(config_fn):
        print(f"Runtime config file: {config_fn}")
        # Just print out the raw yaml for now
        with open(RUNTIME_CONFIG_FN, 'r') as f:
            print(f.read())
        print(f"<end> of {config_fn}")

    return os.path.getmtime(config_fn)


@app.command()
def watch_config(config_fn:str="", poll_delay:float = 1.0):
    """Watches the runtime config file and prints it to the console when it changes.
    """
    if not config_fn:
        config_fn = RUNTIME_CONFIG_FN
    last_updated = 0  # set to 0 to force initial display
    while True:
        last_updated = display_config_if_updated(config_fn, last_updated=last_updated)
        time.sleep(poll_delay)
        


@app.command()
def start(config:str = RUNTIME_CONFIG_FN):
    """Starts the Groundlight runtime.
    Parses the config YAML and launches all the control loops."""
    conductor.start_processes(config_fn=config)


@app.command()
def stop():
    """Stops the Groundlight runtime.
    Stops all the control loops."""
    conductor.stop_processes()


@app.command()
def start(config:str = RUNTIME_CONFIG_FN):
    """Parses the config YAML and returns the parsed config."""
    return conductor.parse_config(config_fn=config)


@app.command()
def restart():
    """Restarts the Groundlight runtime.
    Stops all the control loops and then starts them again."""
    #TODO: Send a signal instead
    conductor.stop_processes()
    conductor.start_processes()


def climain():
    app()

if __name__ == "__main__":
    climain()