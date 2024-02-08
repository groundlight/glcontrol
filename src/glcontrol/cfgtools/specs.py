from glcontrol.cfgtools.base import Parseable
from pydantic import BaseModel


class CameraSpec(BaseModel, Parseable):
    name: str
    type: str
    url: str

    model_config = {'extra': 'forbid'}


class GLControlSpec(BaseModel, Parseable):
    """Pydantic model for the main config files."""
    version: str = "0.0"
    cameras: list[CameraSpec] = []
    detectors: list = []
    controls: list = []

class GLControlConfigFile(BaseModel, Parseable):
    glcontrol: GLControlSpec
