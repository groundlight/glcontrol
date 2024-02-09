import logging
import multiprocessing

from glcontrol.cfgtools.specs import GLControlSpec, GLControlManifest


logger = logging.getLogger(__name__)


def start_processes(config_fn: str):
    spec: GLControlSpec = GLControlManifest.from_file(config_fn).glcontrol
    detectors = list(filter(lambda d: d["config"]["enabled"], spec.detectors))
    if len(detectors) == 0:
        logger.error("No detectors are enabled")
        return
    detector_photo_queues = [multiprocessing.Queue(1) for _ in detectors]
    detector_grab_notify_queues = [multiprocessing.Queue(1) for _ in detectors]
    detector_processes = []
    websocket_metadata_queue = multiprocessing.Queue(1)  # TODO: This is not working.
    websocket_cancel_queue = multiprocessing.Queue(1)  # TODO: This is not working.
    for i in range(len(detectors)):
        process = multiprocessing.Process(
            target=run_process,
            args=(
                i,
                logger,
                detectors[i],
                detector_grab_notify_queues[i],
                detector_photo_queues[i],
                websocket_metadata_queue,
                websocket_cancel_queue,
            ),
        )
        detector_processes.append(process)
        process.start()
