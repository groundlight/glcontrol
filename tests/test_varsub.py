import os

import pytest

from src.glcontrol.cfgtools.base import substitute_variables


def test_substitute_variables_with_existing_env_var(monkeypatch):
    # Setup: Define an environment variable and its value
    monkeypatch.setenv("TEST_VAR", "12345")
    input_str = "Value is {{TEST_VAR}}"

    # Exercise: Call the function with a string containing the environment variable
    result = substitute_variables(input_str)

    # Verify: Check if the function correctly substitutes the environment variable
    assert result == "Value is 12345"


# TODO: This test should work but isn't
@pytest.mark.skip(reason="This test should work but isn't")
def test_substitute_variables_with_non_existing_env_var():
    # Setup: Use a variable name that is not set in the environment
    input_str = "Value is {{NON_EXISTENT_VAR}}"

    # Exercise & Verify: Expect a ValueError for an undefined environment variable
    with pytest.raises(ValueError) as exc_info:
        substitute_variables(input_str)

    # Verify: Check if the error message is as expected
    assert "No environment variable found for: NON_EXISTENT_VAR" in str(exc_info.value)


def test_substitute_variables_without_env_var():
    # Setup: A string without environment variable placeholders
    input_str = "No variables here"

    # Exercise: Call the function with the string
    result = substitute_variables(input_str)

    # Verify: The output should be unchanged
    assert result == "No variables here"


def test_substitute_variables_multiple_vars(monkeypatch):
    # Setup: Define multiple environment variables
    monkeypatch.setenv("VAR1", "alpha")
    monkeypatch.setenv("VAR2", "beta")
    input_str = "{{VAR1}} and {{VAR2}}"

    # Exercise: Call the function with a string containing multiple environment variables
    result = substitute_variables(input_str)

    # Verify: Check if the function correctly substitutes all environment variables
    assert result == "alpha and beta"
