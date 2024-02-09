import json

from pydantic_core import ValidationError
import yaml


class ParsingException(ValueError):
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


class Parseable:
    """A mixin for pydantic BaseModel that adds a parse method from a file."""

    @classmethod
    def from_file(cls, config_fn: str) -> "Parseable":
        """Loads the config file which is YAML and returns the parsed config."""
        with open(config_fn, "r") as f:
            raw = yaml.safe_load(f)

        try:
            return cls(**raw)
        except ValidationError as e:
            msg = "\n".join(pydantic_err_to_friendly(e))
            raise ParsingException(f"Failed to parse {config_fn}: {msg}") from e
