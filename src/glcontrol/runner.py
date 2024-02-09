import framegrab

from glcontrol.cfgtools.specs import GLControlSpec


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
            print(f"Setting up camera: {camera.name}")
            print(f"  input_type: {camera.input_type}")
            print(f"  id: {camera.id}")
            print(f"  options: {camera.options}")
            camera_d = camera.model_dump()
            grabber = framegrab.FrameGrabber.create_grabber(camera_d)
            self._grabbers.append(grabber)
