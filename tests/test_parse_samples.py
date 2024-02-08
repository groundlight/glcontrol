import os

import glcontrol.cfgtools.base as cfgtools


def _test_parse_sample(fn:str):
    out = cfgtools.parse_config_file(fn)
    assert out is not None, f"Failed to parse {fn}"


def test_parse_samples():
    # find the directory we're in
    dir = os.path.dirname(os.path.realpath(__file__))
    samples_dir = f"{dir}/../samples/"
    # find the sample files, which are .yaml
    files = [f for f in os.listdir(samples_dir) if f.endswith(".yaml")]
    assert len(files) > 0, f"No sample files found in {samples_dir}"
    for f in files:
        _test_parse_sample(f"{samples_dir}/{f}")

