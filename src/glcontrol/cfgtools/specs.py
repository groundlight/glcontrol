from enum import Enum

from pydantic import BaseModel, Field

from glcontrol.cfgtools.base import Parseable


class CameraSpec(BaseModel, Parseable):
    name: str
    input_type: str
    id: dict
    options: dict = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class DetectorModality(str, Enum):
    """Defines the options available for the modality of a detector.
    Currently this is only binary.
    """

    binary = "binary"


class DetectorSpec(BaseModel, Parseable):
    name: str
    modality: DetectorModality = DetectorModality.binary
    query: str
    confidence_threshold: float | None = None

    model_config = {"extra": "forbid"}


# TODO: change the name to reflect the new term "processors"
# or whatever we settle on.
class ControlLoopSpec(BaseModel, Parseable):
    name: str
    inputs: list
    type: str
    options: dict = Field(default_factory=dict)


class GLControlSpec(BaseModel, Parseable):
    """Pydantic model for the main config files."""

    image_sources: list[CameraSpec] = []
    detectors: list[DetectorSpec] = []
    processors: list[ControlLoopSpec] = []

    model_config = {"extra": "forbid"}


class GLControlManifest(BaseModel, Parseable):
    version: str = "0.0"
    glcontrol: GLControlSpec
    metadata: dict = {}

    model_config = {"extra": "forbid"}
