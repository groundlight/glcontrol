from enum import Enum

from pydantic import BaseModel

from glcontrol.cfgtools.base import Parseable


class CameraSpec(BaseModel, Parseable):
    name: str
    input_type: str
    id: dict
    options: dict = {}

    model_config = {"extra": "forbid"}


class DetectorModality(str, Enum):
    binary = "binary"


class DetectorSpec(BaseModel, Parseable):
    name: str
    modality: DetectorModality = DetectorModality.binary
    query: str
    confidence_threshold: float | None = None

    model_config = {"extra": "forbid"}


class ControlLoopSpec(BaseModel, Parseable):
    name: str
    type: str
    camera: str
    detector: str
    poll_delay: str


class GLControlSpec(BaseModel, Parseable):
    """Pydantic model for the main config files."""

    cameras: list[CameraSpec] = []
    detectors: list[DetectorSpec] = []
    controls: list[ControlLoopSpec] = []


class GLControlManifest(BaseModel, Parseable):
    version: str = "0.0"
    glcontrol: GLControlSpec
    metadata: dict = {}

    model_config = {"extra": "forbid"}
