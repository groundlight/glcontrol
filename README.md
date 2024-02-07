# GLControl: Declarative CV control loops with Groundlight


GL control lets you create visual control systems simply by writing YAML configuration files.  Then `glcontrol` interprets these files, creates ML detectors in the cloud using Groundlight based on your natural language instructions, uses [`framegrab`](https://github.com/groundlight/framegrab) to capture images from your camera, and then runs a control loop to capture images, analyze them, and respond to the results.

Here's a simple example of a config to send a text message if your garage door is open:
    
```yaml
cameras:
  # define cameras using `framegrab` syntax
  - name: in-garage-rtsp
    type: rtsp
    url: rtsp://admin:admin@192.168.1.55:554

detectors:
  - name: garage-door
    modality: binary
    query: "Is the garage door open?"
    instructions: 
      - note: "If the image is too dark, answer NO."

control:
  - name: garage-door
    camera: in-garage-rtsp
    detector: garage-door
    poll:
        every: 60
    motion-detection:
        enabled: True

triggers:
  - action: send-sms
    control-loop: garage-door
    condition:
        value: YES
        trigger-type: on-change
        debounce:
            # Alert me at most once per hour
            min-delay: 3600

actions:
  - name: send-sms
    type: sms
    to: 206-555-5555
    message: "Your garage door is open!"
```

To make it work, just save it as a file like `garage-door.yaml`, set your API token, and run it:

```bash
export GROUNDLIGHT_API_TOKEN=api_your_token
glcontrol garage-door.yaml
```

## Status

Note: this is a work in progress.  Not all features are implemented yet.