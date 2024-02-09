import logging

import framegrab

from glcontrol.cfgtools.specs import GLControlSpec


logger = logging.getLogger(__name__)

class SpecRunner:
    """Interprets a GLControlSpec and runs the control loops."""

    _spec: GLControlSpec
    _grabbers: list[framegrab.FrameGrabber]

    def __init__(self, spec: GLControlSpec):
        self._spec = spec
        self._setup_cameras()

    def _setup_cameras(self):
        """Instantiate the cameras using framegrab"""
        self._grabbers = []
        for camera in self._spec.cameras:
            logger.info(f"Setting up camera: {camera.name}")
            logger.debug(f"  input_type: {camera.input_type}")
            # Don't log id, because it can have passwords if it's rtsp
            logger.debug(f"  options: {camera.options}")
            camera_d = camera.model_dump()
            grabber = framegrab.FrameGrabber.create_grabber(camera_d)
            self._grabbers.append(grabber)
