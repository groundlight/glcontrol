from enum import Enum
from glcontrol.cfgtools.base import Parseable
from pydantic import BaseModel


class CameraSpec(BaseModel, Parseable):
    name: str
    input_type: str
    id: dict
    options: dict = {}

    model_config = {'extra': 'forbid'}


class DetectorModality(str, Enum):
    binary = "binary"


class DetectorSpec(BaseModel, Parseable):
    name: str
    modality: DetectorModality = DetectorModality.binary
    query: str
    confidence_threshold: float | None = None

    model_config = {'extra': 'forbid'}


class GLControlSpec(BaseModel, Parseable):
    """Pydantic model for the main config files."""
    cameras: list[CameraSpec] = []
    detectors: list = [DetectorSpec]
    controls: list = []


class GLControlManifest(BaseModel, Parseable):
    version: str = "0.0"
    glcontrol: GLControlSpec
    metadata: dict = {}

    model_config = {'extra': 'forbid'}