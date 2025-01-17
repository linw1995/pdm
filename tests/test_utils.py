import pathlib
import re
import sys

import pytest

from pdm import utils


@pytest.mark.parametrize(
    "given,expected",
    [
        ("test", "test"),
        ("", ""),
        ("${FOO}", "hello"),
        ("$FOO", "$FOO"),
        ("${BAR}", "${BAR}"),
        ("%FOO%", "%FOO%"),
        ("${FOO}_${FOO}", "hello_hello"),
    ],
)
def test_expand_env_vars(given, expected, monkeypatch):
    monkeypatch.setenv("FOO", "hello")
    assert utils.expand_env_vars(given) == expected


@pytest.mark.parametrize(
    "given,expected",
    [
        ("https://example.org/path?arg=1", "https://example.org/path?arg=1"),
        (
            "https://${FOO}@example.org/path?arg=1",
            "https://hello@example.org/path?arg=1",
        ),
        (
            "https://${FOO}:${BAR}@example.org/path?arg=1",
            "https://hello:wo%3Arld@example.org/path?arg=1",
        ),
        (
            "https://${FOOBAR}@example.org/path?arg=1",
            "https://%24%7BFOOBAR%7D@example.org/path?arg=1",
        ),
    ],
)
def test_expend_env_vars_in_auth(given, expected, monkeypatch):
    monkeypatch.setenv("FOO", "hello")
    monkeypatch.setenv("BAR", "wo:rld")
    assert utils.expand_env_vars_in_auth(given) == expected


def test_find_python_in_path(tmp_path):

    assert utils.find_python_in_path(sys.executable) == pathlib.Path(sys.executable)

    posix_path_to_executable = pathlib.Path(sys.executable).as_posix().lower()
    if sys.platform == "darwin":
        found_version_of_executable = re.split(
            r"(python@[\d.]*\d+)", posix_path_to_executable
        )
        posix_path_to_executable = "".join(found_version_of_executable[0:2])
    assert (
        utils.find_python_in_path(sys.prefix)
        .as_posix()
        .lower()
        .startswith(posix_path_to_executable)
    )

    assert not utils.find_python_in_path(tmp_path)
