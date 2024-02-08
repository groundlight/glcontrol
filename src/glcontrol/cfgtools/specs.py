from glcontrol.cfgtools.base import Parseable
from pydantic import BaseModel


class GLControlSpec(BaseModel, Parseable):
    """Pydantic model for the main config files."""
    version: str = "0.0"
    cameras: list
    detectors: list
    controls: list

class GLControlConfigFile(BaseModel, Parseable):
    glcontrol: GLControlSpec
