import logging
from typing import Dict, Type

import framegrab
from groundlight import Groundlight

from glcontrol.cfgtools.specs import CameraSpec, ControlLoopSpec, DetectorSpec, GLControlSpec

logger = logging.getLogger(__name__)


def sdk_connect() -> Groundlight:
    """Connect to the Groundlight SDK."""
    # This automatically looks in the environment variables
    # for auth info and endpoint.
    return Groundlight()


def parse_time_str(time_str: str) -> float:
    """Parse a time string like '1 min' or '30 sec' into seconds.
    If it's just a raw number, it will be interpreted as seconds.
    """
    # Check for just seconds first
    try:
        return float(time_str)
    except ValueError:
        pass  # look for valid time strings
    # Valid format is "<number> <unit>"
    parts = time_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid time string: {time_str}")
    num, unit = parts
    try:
        num = float(num)
    except ValueError:
        raise ValueError(f"Invalid time string: {time_str}")
    if unit in ("s", "sec", "second", "seconds"):
        return num
    elif unit in ("m", "min", "minute", "minutes"):
        return num * 60
    elif unit in ("h", "hr", "hour", "hours"):
        return num * 60 * 60
    else:
        raise ValueError(f"Unrecognized time string: {time_str}")


class DetectorRT:
    """Interprets a DetectorSpec and creates it in the SDK.
    This class also stores a registry of all the detectors by name.
    """

    registry: dict[str, "DetectorRT"] = {}

    def __init__(self, spec: DetectorSpec, sdk: Groundlight):
        self.sdk = sdk
        self.spec = spec
        self.detector = self._init_detector()
        self.registry[spec.name] = self
        self._last_result = None

    @classmethod
    def by_name(cls, name: str) -> "DetectorRT":
        """Get a detector by name."""
        return cls.registry[name]

    def _init_detector(self) -> "Detector":
        """Instantiate the detector using the spec."""
        out = self.sdk.get_or_create_detector(
            name=self.spec.name, query=self.spec.query, confidence_threshold=self.spec.confidence_threshold
        )
        return out

    def __repr__(self):
        d_id = self.detector.id if self.detector else "None"
        return f"DetectorRT('{self.spec.name}', id={d_id})"

    def store_result(self, result: dict):
        """Store the result in the detector."""
        self._last_result = result

class ImageSourceRT:
    """Interprets a CameraSpec and creates it using framegrab.
    This class also stores a registry of all the cameras by name.
    """

    registry: dict[str, "ImageSourceRT"] = {}

    def __init__(self, spec: CameraSpec):
        self.spec = spec
        logger.info(f"Setting up camera: {spec.name}")
        camera_d = spec.model_dump()
        self.grabber = framegrab.FrameGrabber.create_grabber(camera_d)
        self.registry[spec.name] = self

    @classmethod
    def by_name(cls, name: str) -> "ImageSourceRT":
        """Get a camera by name."""
        return cls.registry[name]

    def frame_grab(self) -> "framegrab.Frame":
        """Grab a frame from the camera."""
        frame = self.grabber.grab()
        return frame

    def __repr__(self):
        return f"ImageSourceRT('{self.spec.name}')"


class ControlLoopRegistry(type):
    """
    Metaclass for automatically registering subclasses of ControlLoop.
    """

    registry: Dict[str, Type["ControlLoop"]] = {}

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        new_class = super().__new__(cls, name, bases, attrs)
        # Only attempt to register subclasses with a defined registry_name attribute
        if bases:
            try:
                registry_name = attrs["registry_name"]
                assert len(registry_name) > 0
            except (KeyError, AssertionError) as e:
                raise ValueError("ControlLoop classes must have registry_name") from e
            if registry_name in cls.registry:
                raise ValueError(f"Duplicate registration for '{registry_name}'")
            cls.registry[registry_name] = new_class
        return new_class


class ControlLoop(metaclass=ControlLoopRegistry):
    """
    Base class for all control loops.
    """

    registry_name: str = "abstract-base"

    def __init__(self, spec: dict, sdk: Groundlight):
        self.spec = spec
        self.sdk = sdk

    def __repr__(self):
        return f"ControlLoop<type={self.registry_name}, name='{self.spec['name']}'>"

    @staticmethod
    def from_spec(spec: ControlLoopSpec, sdk: Groundlight) -> "ControlLoop":
        """
        Factory method to instantiate subclasses based on their registration name.
        """
        name = spec.type
        if name not in ControlLoopRegistry.registry:
            raise ValueError(f"Unknown control type '{name}'")
        cls = ControlLoopRegistry.registry[name]
        return cls(spec, sdk)

    def run_loop(self):
        """
        Main loop for the control loop.
        """
        raise NotImplementedError("ControlLoop subclasses must implement run_loop")

    def _setup_camera(self) -> ImageSourceRT:
        """
        Looks up the image source named in the spec.
        """
        return ImageSourceRT.by_name(self.spec.camera)

    def _setup_detector(self) -> DetectorRT:
        """
        Looks up the detector named in the spec.
        """
        return DetectorRT.by_name(self.spec.detector)


class SimpleCameraDetectorLoop(ControlLoop):
    registry_name = "simple-camera-detector"  # Explicitly defining the registration name

    def __init__(self, spec: dict, sdk: Groundlight):
        super().__init__(spec, sdk)
        self.camera = self._setup_camera()
        self.detector_rt = self._setup_detector()
        self.poll_delay = parse_time_str(self.spec.get("poll_delay", "60 s"))

    def run_loop(self):
        while True:
            frame = self.camera.grab()
            # TODO: make the `ask_*` type configurable
            result = self.sdk.ask_ml(self.detector_rt.detector, frame)
            logger.debug(f"Got result: {result}")
            self.detector_rt.store_result(result)


class SpecRunner:
    """Interprets a GLControlSpec and runs the control loops."""

    spec: GLControlSpec
    sdk: Groundlight
    image_sources: list[ImageSourceRT]
    detectors: list[DetectorRT]
    control_loops: list[ControlLoop]

    def __init__(self, spec: GLControlSpec):
        self.spec = spec
        self.sdk = sdk_connect()
        self.image_sources = self._setup_image_sources()
        self.detectors = self._setup_detectors()
        self.control_loops = self._setup_control_loops()

    def _setup_image_sources(self) -> list[ImageSourceRT]:
        """Instantiate the cameras using framegrab"""
        out = []
        for camera in self.spec.cameras:
            logger.info(f"Setting up camera: {camera.name}")
            new_camera = ImageSourceRT(camera)
            out.append(new_camera)
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

    def _setup_control_loops(self) -> list[ControlLoop]:
        """Instantiate the control loops using the spec."""
        out = []
        for control in self.spec.controls:
            logger.info(f"Setting up control loop: {control.name}")
            new_loop = ControlLoop.from_spec(control, self.sdk)
            out.append(new_loop)
        return out
