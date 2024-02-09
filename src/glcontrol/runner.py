import logging

import framegrab
from groundlight import Groundlight

from glcontrol.cfgtools.specs import DetectorSpec, GLControlSpec

logger = logging.getLogger(__name__)


def sdk_connect() -> Groundlight:
    """Connect to the Groundlight SDK."""
    # This automatically looks in the environment variables
    # for auth info and endpoint.
    return Groundlight()


class DetectorRT:
    """Interprets a DetectorSpec and creates it in the SDK."""

    def __init__(self, spec: DetectorSpec, sdk: Groundlight):
        self.sdk = sdk
        self.spec = spec
        self.detector = None
        self.sdk_init()

    def sdk_init(self):
        """Instantiate the detector using the spec."""
        self.detector = self.sdk.get_or_create_detector(
            name=self.spec.name, query=self.spec.query, confidence_threshold=self.spec.confidence_threshold
        )

    def __repr__(self):
        d_id = self.detector.id if self.detector else "None"
        return f"DetectorRT("{self.spec.name}"", id={d_id})"


class SpecRunner:
    """Interprets a GLControlSpec and runs the control loops."""

    sdk: Groundlight
    spec: GLControlSpec
    grabbers: list[framegrab.FrameGrabber]

    def __init__(self, spec: GLControlSpec):
        self.spec = spec
        self.grabbers = self._setup_grabbers()
        self.sdk = sdk_connect()
        self.detectors = self._setup_detectors()

    def _setup_grabbers(self) -> list[framegrab.FrameGrabber]:
        """Instantiate the cameras using framegrab"""
        out = []
        for camera in self.spec.cameras:
            logger.info(f"Setting up camera: {camera.name}")
            camera_d = camera.model_dump()
            grabber = framegrab.FrameGrabber.create_grabber(camera_d)
            out.append(grabber)
        return out

    def _setup_detectors(self) -> list[DetectorRT]:
        """Instantiate the detectors using the spec."""
        out = []
        for detector in self.spec.detectors:
            logger.info(f"Setting up detector: {detector.name}")
            new_detector = DetectorRT(detector, self.sdk)
            out.append(new_detector)
            print(f"Found detector: {new_detector}")
        return out
