import yaml


class ParsingException(ValueError):
    """Raised when the config file is invalid."""

    pass


class Parseable:
    """A mixin for pydantic BaseModel that adds a parse method from a file."""

    @classmethod
    def from_file(cls, config_fn: str) -> "Parseable":
        """Loads the config file which is YAML and returns the parsed config."""
        with open(config_fn, "r") as f:
            raw = yaml.safe_load(f)

        try:
            return cls(**raw)
        except Exception as e:
            raise ParsingException(f"Failed to parse {config_fn}: {e}") from e
