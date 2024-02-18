# GLControl: Declarative Visual Automation

GL control lets you create visual control systems simply by writing YAML configuration files.  Then `glcontrol` interprets these files, creates ML detectors in the cloud using Groundlight based on your natural language instructions, uses [`framegrab`](https://github.com/groundlight/framegrab) to capture images from your camera, and then runs a control loop to capture images, analyze them, and respond to the results.

Here's a simple example of a config to send a text message if the dumpster is over-filled:
    
```yaml
glcontrol:
  cameras:
    # define cameras using `framegrab` syntax
    - name: back-alley-rtsp
      type: rtsp
      url: rtsp://admin:admin@192.168.1.33:554

  detectors:
    - name: dumpster-overflowing
      modality: binary
      query: "Is the dumpster overflowing?"

  processors:
    - name: dumpster-overflowing
      type: simple-camera-detector
      inputs:
        - camera: back-alley-rtsp
      options:
        motion_detection: enabled
        poll: every 60 sec
        detector: is-dumpster-overflowing
```

To make it all work, just save it as a file like `dumpster-overflowing.yaml`, set your API token, and run it:

```bash
pip install glcontrol
vi ./dumpster-overflowing.yaml
export GROUNDLIGHT_API_TOKEN=api_your_token
glcontrol ./dumpster-overflowing.yaml
```

## Status

Note: this is a work in progress.  Not all documented features are implemented yet.


## CLI

You can run `glcontrol` from the command line to start a control loop.  It will read the config file, create detectors, and start the control loop.  Generally you need to supply the name of the config yaml, but you can also set it
as the `GLCONTROL_CONFIG` environment variable.

