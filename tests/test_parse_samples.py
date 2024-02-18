import os

import glcontrol.cfgtools.base as cfgtools
from glcontrol.cfgtools.specs import GLControlManifest


def _test_parse_spec(fn: str) -> GLControlManifest:
    out = GLControlManifest.from_file(fn)
    assert out is not None, f"Failed to parse {fn}"
    return out


def test_parse_good_samples(monkeypatch):
    monkeypatch.setenv("RTSP_PASSWORD", "secret")
    # find the directory we're in
    basedir = os.path.dirname(os.path.realpath(__file__))
    samples_dir = f"{basedir}/good-samples/"
    # find the sample files, which are .yaml
    files = [f for f in os.listdir(samples_dir) if f.endswith(".yaml")]
    assert len(files) > 0, f"No sample files found in {samples_dir}"
    for f in files:
        _test_parse_spec(f"{samples_dir}/{f}")


def test_parse_bad_samples():
    # find the directory we're in
    basedir = os.path.dirname(os.path.realpath(__file__))
    samples_dir = f"{basedir}/bad-samples/"
    # find the sample files, which are .yaml
    files = [f for f in os.listdir(samples_dir) if f.endswith(".yaml")]
    assert len(files) > 0, f"No bad sample files found in {samples_dir}"
    for f in files:
        try:
            out = _test_parse_spec(f"{samples_dir}/{f}")
            assert False, f"Expected to fail parsing {f}, but instead got a valid {out}"
        except cfgtools.ParsingError as e:
            print(f"Successfully failed parsing {f}: {e}")
