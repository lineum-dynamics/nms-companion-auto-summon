"""Prototype a noninteractive host import of the reviewed pyMHF version.

This helper does not start pyMHF, load a mod, attach to a process or register
hooks. It is not wired into a launcher. Its result says nothing about the
separate interpreter inside a game or the lifecycle of ``run_module``.
"""

from importlib import import_module, metadata


FRAMEWORK_VERSION = "0.2.4"


def import_pymhf_noninteractive():
    """Import pyMHF with explicit dummy terminal devices, then restore context.

pyMHF constructs questionary prompts at import time even when its caller will
not use its interactive CLI. Public prompt_toolkit devices avoid asking Windows
for a console screen buffer. They do not skip framework initialization or make
interactive prompts usable. No test environment flags are set.
"""
    if metadata.version("pymhf") != FRAMEWORK_VERSION:
        raise RuntimeError("The host import prototype requires pyMHF 0.2.4")

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import DummyInput
    from prompt_toolkit.output import DummyOutput

    with create_app_session(input=DummyInput(), output=DummyOutput()):
        return import_module("pymhf")
