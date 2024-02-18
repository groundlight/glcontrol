import json
import os
import re

import yaml
from pydantic_core import ValidationError


class ParsingError(ValueError):
    """Raised when the config file is invalid."""


def pydantic_err_to_friendly(err: ValidationError) -> list[str]:
    """Converts a pydantic ValidationError into a user-friendly message."""
    err_data = json.loads(err.json())
    msgs = []
    for err_datum in err_data:
        dotloc = ".".join([str(item) for item in err_datum["loc"]])
        if err_datum["type"] == "extra_forbidden":
            msg = f"Unexpected field `{err_datum['loc'][-1]}` at {dotloc}"
        else:
            msg = f"{dotloc}: {err_datum['msg']}"
        msgs.append(msg)
    return msgs


def substitute_variables(raw_str: str, filename: str) -> str:
    """Substitutes environment variables in the raw string.
    Looks for patterns like {{VARNAME}} and replaces it with the value of the environment variable VARNAME.
    """
    pattern = re.compile(r"\{\{(\w+)\}\}")  # Matches {{VARNAME}}
    result = raw_str
    matches = pattern.findall(raw_str)
    for match in matches:
        var_name = match
        if var_name in os.environ:
            print(f"Found environment variable: {var_name}, replacing it.")
            env_value = os.environ[var_name]
            result = result.replace("{{" + var_name + "}}", env_value)
        else:
            raise ValueError(f"Missing environment variable {var_name} which is referenced in {filename}")
    return result


class Parseable:
    """A mixin for pydantic BaseModel that adds a parse method from a file."""

    @classmethod
    def from_file(cls, config_path: str) -> "Parseable":
        """Loads the config file which is YAML and returns the parsed config."""
        with open(config_path, "r") as f:
            # first load it as a string
            raw_str = f.read()

        # Now call variable substitution
        raw_str = substitute_variables(raw_str, config_path)

        # Now parse it into a dict
        raw = yaml.safe_load(raw_str)

        try:
            return cls(**raw)
        except ValidationError as e:
            msg = "\n".join(pydantic_err_to_friendly(e))
            raise ParsingError(f"Failed to parse {config_path}: {msg}") from e
        except Exception as e:
            raise ParsingError(f"Failed to parse {config_path}: {e}") from e
