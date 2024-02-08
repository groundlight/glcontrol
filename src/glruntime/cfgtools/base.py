import yaml


class RuntimeConfig(dict):
    """Just a dummy class to represent the runtime configuration."""
    pass


def parse_config_file(config_fn: str) -> RuntimeConfig:
    """Loads the config file which is YAML and returns the parsed config."""
    with open(config_fn, "r") as f:
        config = yaml.safe_load(f)
    return config
