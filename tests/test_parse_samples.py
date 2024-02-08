import os

import glcontrol.cfgtools.base as cfgtools
from glcontrol.cfgtools.specs import GLControlConfigFile


def _test_parse_spec(fn: str) -> GLControlConfigFile:
    out = GLControlConfigFile.from_file(fn)
    assert out is not None, f"Failed to parse {fn}"
    return out


def test_parse_good_samples():
    # find the directory we're in
    dir = os.path.dirname(os.path.realpath(__file__))
    samples_dir = f"{dir}/good-samples/"
    # find the sample files, which are .yaml
    files = [f for f in os.listdir(samples_dir) if f.endswith(".yaml")]
    assert len(files) > 0, f"No sample files found in {samples_dir}"
    for f in files:
        _test_parse_spec(f"{samples_dir}/{f}")


def test_parse_bad_samples():
    # find the directory we're in
    dir = os.path.dirname(os.path.realpath(__file__))
    samples_dir = f"{dir}/bad-samples/"
    # find the sample files, which are .yaml
    files = [f for f in os.listdir(samples_dir) if f.endswith(".yaml")]
    assert len(files) > 0, f"No sample files found in {samples_dir}"
    for f in files:
        try:
            _test_parse_spec(f"{samples_dir}/{f}")
            assert False, f"Expected to fail parsing {f}"
        except cfgtools.ParsingException as e:
            pass
