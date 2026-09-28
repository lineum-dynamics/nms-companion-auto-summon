"""Owned startup for the isolated portable interpreter; never access a game.

The owned host/prelude imports this explicitly, with bytecode already disabled,
in both an ordinary host and a fresh pyrun_injected interpreter. Automatic site
import is disabled so vendor .pth files cannot run before that flag is set.
Vendor wheel files stay intact.
"""

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
_dll_directories = [
    os.add_dll_directory(str(ROOT)),
    os.add_dll_directory(str(ROOT / "Lib/site-packages/pywin32_system32")),
]

# pyMHF creates questionary prompts during import. This process-owned dummy
# session never reads a terminal and remains alive through target initialization.
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import DummyInput
from prompt_toolkit.output import DummyOutput

_terminal_session = create_app_session(input=DummyInput(), output=DummyOutput())
_terminal_session.__enter__()
PORTABLE_BOOTSTRAP_READY = True
