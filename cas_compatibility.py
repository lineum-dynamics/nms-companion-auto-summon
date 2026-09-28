"""Host-only compatibility checks and localized launch failures.

Importing performs no file, process, DLL, framework or UI operations. These
checks never inject, launch, stop or modify a game. The queried executable is
obtained from the actual injection handle, not from a process-name search.
Disk hashes do not establish integrity of the entire mapped executable.
"""

from collections import Counter
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
from string import Formatter
import sys


SUPPORTED_GAME_SHA256 = "b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb"
STEAM_BUILD = "25442159"
GAME_RELEASE = "Cosmos 7.04"
FRAMEWORK_VERSION = "0.2.4"
PROFILE = {"schema_version": 1, "steam_build": STEAM_BUILD,
           "game_release": GAME_RELEASE, "exe_sha256": SUPPORTED_GAME_SHA256,
           "framework_version": FRAMEWORK_VERSION}
WARNING_KEYS = ("launcher.blocked_title", "launcher.unsupported_game", "launcher.unreadable_game",
                "launcher.game_required", "launcher.invalid_package", "launcher.wrong_framework",
                "launcher.game_changed", "launcher.game_running", "launcher.preflight_passed")
WARNING_FALLBACKS = {
    "launcher.blocked_title": "Companion Auto Summon for No Man's Sky could not start",
    "launcher.invalid_package": "The mod package is incomplete or inconsistent. Extract a complete matching package and try again.",
}
LOCALES = ("en", "fr", "it", "de", "es-ES", "nl", "ja", "ko", "pl", "pt-PT",
           "pt-BR", "ru", "zh-Hans", "zh-Hant")
LOCALES_DIRECTORY = Path(__file__).absolute().parent / "locales"
MAX_PATH_CHARACTERS = 32768
MAX_CATALOG_BYTES = 65536
MAX_TEXT_BYTES = 1024


class CompatibilityError(RuntimeError):
    """Stable external failure category; diagnostic text never includes paths."""

    def __init__(self, key, **fields):
        if key not in WARNING_KEYS:
            key = "launcher.invalid_package"
            fields = {}
        self.key = key
        self.fields = dict(fields)
        super().__init__(key)


def _absolute_path(value, error_key):
    try:
        raw = os.fspath(value)
        if (type(raw) is not str or not raw or len(raw) >= MAX_PATH_CHARACTERS
                or any(ord(character) < 32 for character in raw)):
            raise ValueError
        path = Path(raw)
        if not path.is_absolute():
            raise ValueError
        return path
    except (TypeError, ValueError, OSError):
        raise CompatibilityError(error_key) from None


def _verify_executable(value, *, missing_key):
    path = _absolute_path(value, missing_key)
    try:
        path = path.resolve(strict=True)
        if not path.is_file():
            raise CompatibilityError(missing_key)
        if path.name.casefold() != "nms.exe":
            raise CompatibilityError("launcher.unsupported_game")
        with path.open("rb") as binary:
            before = os.fstat(binary.fileno())
            digest = hashlib.file_digest(binary, "sha256").hexdigest()
            after = os.fstat(binary.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise CompatibilityError("launcher.game_changed")
    except CompatibilityError:
        raise
    except FileNotFoundError:
        raise CompatibilityError(missing_key) from None
    except (OSError, ValueError, RuntimeError):
        raise CompatibilityError("launcher.unreadable_game") from None
    if digest != SUPPORTED_GAME_SHA256:
        raise CompatibilityError("launcher.unsupported_game")
    return path


def verify_game_directory(directory):
    """Return the canonical supported NMS.exe; never repair or create files."""
    game = _absolute_path(directory, "launcher.game_required")
    return _verify_executable(game / "Binaries" / "NMS.exe", missing_key="launcher.game_required")


def _query_target_image(handle, api=None):
    """Query one actual handle with a bounded Unicode buffer; no PID reopen."""
    import ctypes as C
    from ctypes import wintypes as W
    if type(handle) is not int or not 0 < handle < (1 << 64) - 1:
        raise CompatibilityError("launcher.unreadable_game")
    if api is None:
        if os.name != "nt":
            raise CompatibilityError("launcher.unreadable_game")
        kernel = C.WinDLL("kernel32", use_last_error=True)
        api = kernel.QueryFullProcessImageNameW
        api.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]
        api.restype = W.BOOL
    buffer = C.create_unicode_buffer(MAX_PATH_CHARACTERS)
    size = W.DWORD(MAX_PATH_CHARACTERS)
    if not api(handle, 0, buffer, C.byref(size)):
        raise CompatibilityError("launcher.unreadable_game")
    # Windows counts UTF-16 code units, excluding NUL; Python counts code
    # points. Refuse truncation, embedded NUL and inconsistent results.
    text = buffer.value
    try:
        code_units = len(text.encode("utf-16-le")) // 2
    except UnicodeError:
        raise CompatibilityError("launcher.unreadable_game") from None
    if not 0 < size.value < MAX_PATH_CHARACTERS or code_units != size.value:
        raise CompatibilityError("launcher.unreadable_game")
    return text


def verify_target(handle, expected_executable=None, query=None):
    """Rehash the actual target before each DLL injection; return its Path.

    Optional query is a callable(handle) -> absolute Unicode path, for owned
    offline tests. The maintained launchers use the default Windows query.
    This function does not call or import any injector.
    """
    if type(handle) is not int or not 0 < handle < (1 << 64) - 1:
        raise CompatibilityError("launcher.unreadable_game")
    try:
        actual = (query if query is not None else _query_target_image)(handle)
        executable = _verify_executable(actual, missing_key="launcher.unreadable_game")
        if expected_executable is not None:
            try:
                expected = _absolute_path(expected_executable, "launcher.game_changed").resolve(strict=True)
            except (OSError, ValueError, RuntimeError):
                raise CompatibilityError("launcher.game_changed") from None
            if os.path.normcase(str(executable)) != os.path.normcase(str(expected)):
                raise CompatibilityError("launcher.game_changed")
        return executable
    except CompatibilityError:
        raise
    except Exception:
        raise CompatibilityError("launcher.unreadable_game") from None


def verify_framework():
    """Require the isolated framework; foreign libraries can override its bases."""
    try:
        if metadata.version("pymhf") != FRAMEWORK_VERSION:
            raise CompatibilityError("launcher.wrong_framework")
        if tuple(metadata.entry_points().select(group="pymhflib")):
            raise CompatibilityError("launcher.invalid_package")
    except CompatibilityError:
        raise
    except Exception:
        raise CompatibilityError("launcher.wrong_framework") from None
    return True


def _windows_process_names(api=None):
    """Copy one bounded Toolhelp snapshot, including protected process names."""
    import ctypes as C
    from ctypes import wintypes as W
    from types import SimpleNamespace
    class Entry(C.Structure):
        _fields_ = [("size", W.DWORD), ("usage", W.DWORD), ("pid", W.DWORD),
                    ("heap", C.c_size_t), ("module", W.DWORD), ("threads", W.DWORD),
                    ("parent", W.DWORD), ("priority", W.LONG), ("flags", W.DWORD),
                    ("name", W.WCHAR * 260)]
    if api is None:
        if os.name != "nt":
            raise CompatibilityError("launcher.unreadable_game")
        kernel = C.WinDLL("kernel32", use_last_error=True)
        kernel.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
        kernel.CreateToolhelp32Snapshot.restype = W.HANDLE
        for function in (kernel.Process32FirstW, kernel.Process32NextW):
            function.argtypes = [W.HANDLE, C.POINTER(Entry)]
            function.restype = W.BOOL
        kernel.CloseHandle.argtypes = [W.HANDLE]
        kernel.CloseHandle.restype = W.BOOL
        api = SimpleNamespace(CreateToolhelp32Snapshot=kernel.CreateToolhelp32Snapshot,
                              Process32FirstW=kernel.Process32FirstW,
                              Process32NextW=kernel.Process32NextW,
                              CloseHandle=kernel.CloseHandle, get_last_error=C.get_last_error)
    handle = api.CreateToolhelp32Snapshot(2, 0)
    if not handle or handle == C.c_void_p(-1).value:
        raise CompatibilityError("launcher.unreadable_game")
    try:
        entry = Entry()
        entry.size = C.sizeof(entry)
        names = []
        available = api.Process32FirstW(handle, C.byref(entry))
        while available:
            if len(names) >= 65536:
                raise CompatibilityError("launcher.unreadable_game")
            names.append(entry.name)
            available = api.Process32NextW(handle, C.byref(entry))
        if api.get_last_error() != 18 or not names:
            raise CompatibilityError("launcher.unreadable_game")
        return names
    finally:
        if not api.CloseHandle(handle):
            raise CompatibilityError("launcher.unreadable_game")


def game_closed():
    """Unknown process state is never treated as a closed game."""
    try:
        names = _windows_process_names()
        return bool(names) and all(type(name) is str and name and name.casefold() != "nms.exe"
                                   for name in names)
    except Exception:
        return False


def _windows_ui_language(api=None):
    """Read host Windows UI language, never the game's language setting."""
    import ctypes as C
    from ctypes import wintypes as W
    if api is None:
        if os.name != "nt":
            return None
        api = C.WinDLL("kernel32", use_last_error=True)
        api.GetUserDefaultUILanguage.argtypes = []
        api.GetUserDefaultUILanguage.restype = W.WORD
        api.LCIDToLocaleName.argtypes = [W.DWORD, W.LPWSTR, C.c_int, W.DWORD]
        api.LCIDToLocaleName.restype = C.c_int
    buffer = C.create_unicode_buffer(85)  # LOCALE_NAME_MAX_LENGTH, including NUL.
    count = api.LCIDToLocaleName(api.GetUserDefaultUILanguage(), buffer, len(buffer), 0)
    if type(count) is int and 1 < count <= len(buffer) and len(buffer.value) == count - 1:
        return buffer.value
    return None


def _language_code(language):
    if language is None:
        try:
            language = _windows_ui_language()
        except Exception:
            language = None
    if type(language) is not str or len(language) > 85:
        return "en"
    code = language.replace("_", "-").casefold()
    exact = {locale.casefold(): locale for locale in LOCALES}
    if code in exact:
        return exact[code]
    parts = code.split("-")
    if parts[0] in {"en", "fr", "it", "de", "nl", "ja", "ko", "pl", "ru"}:
        return parts[0]
    if parts[0] == "es":
        return "es-ES"
    if parts[0] == "pt":
        return "pt-BR" if len(parts) > 1 and parts[1] == "br" else "pt-PT"
    if parts[0] == "zh":
        if "hant" in parts or len(parts) > 1 and parts[1] in {"tw", "hk", "mo"}:
            return "zh-Hant"
        return "zh-Hans"
    return "en"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate catalog key")
        result[key] = value
    return result


def _placeholders(text):
    result = Counter()
    for _literal, field, spec, conversion in Formatter().parse(text):
        if field is not None:
            if field not in {"build", "version"} or spec or conversion is not None:
                raise ValueError("Unsupported warning placeholder")
            result[field] += 1
    return result


def _warning_catalog(code):
    with (LOCALES_DIRECTORY / (code + ".json")).open("rb") as stream:
        data = stream.read(MAX_CATALOG_BYTES + 1)
    if len(data) > MAX_CATALOG_BYTES:
        raise ValueError("Oversized catalog")
    document = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    if (type(document) is not dict or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1 or document.get("locale") != code
            or document.get("scope") != "native_menu_hud_technology_launcher"
            or document.get("review_status") != ("canonical" if code == "en" else "draft_unreviewed")
            or document.get("native_runtime_integrated") is not False):
        raise ValueError("Invalid catalog metadata")
    messages = document.get("messages")
    if type(messages) is not dict or not set(WARNING_KEYS) <= set(messages) or len(messages) > 256:
        raise ValueError("Incomplete warning catalog")
    result = {}
    for key in WARNING_KEYS:
        entry = messages[key]
        if type(entry) is not dict or set(entry) != {"text", "source_sha256"}:
            raise ValueError("Invalid warning entry")
        text, fingerprint = entry["text"], entry["source_sha256"]
        if (type(text) is not str or not text.strip() or any(ord(char) < 32 for char in text)
                or len(text.encode("utf-8")) > MAX_TEXT_BYTES or type(fingerprint) is not str
                or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None):
            raise ValueError("Invalid warning text")
        expected = Counter({"build": 1}) if key == "launcher.unsupported_game" else (
            Counter({"version": 1}) if key == "launcher.wrong_framework" else Counter())
        if _placeholders(text) != expected:
            raise ValueError("Warning placeholders differ")
        result[key] = entry
    return result


def warning_text(key, language=None, **fields):
    """Render a bounded host message; invalid catalogs yield a generic fallback.

    Explicit unsupported languages, including Czech, select English. Missing or
    malformed requested catalogs do not masquerade as translated messages: only
    the two built-in English package-failure strings are available as fallback.
    """
    fallback_key = "launcher.blocked_title" if key == "launcher.blocked_title" else "launcher.invalid_package"
    try:
        if key not in WARNING_KEYS or set(fields) - {"build", "version"}:
            raise ValueError("Unsupported warning request")
        english = _warning_catalog("en")
        for name, entry in english.items():
            if entry["source_sha256"] != hashlib.sha256(entry["text"].encode("utf-8")).hexdigest():
                raise ValueError("English source fingerprint differs")
            if name in WARNING_FALLBACKS and entry["text"] != WARNING_FALLBACKS[name]:
                raise ValueError("Emergency fallback differs")
        code = _language_code(language)
        selected = english if code == "en" else _warning_catalog(code)
        for name, entry in selected.items():
            if entry["source_sha256"] != english[name]["source_sha256"]:
                raise ValueError("Stale warning translation")
            if code != "en" and entry["text"] == english[name]["text"]:
                raise ValueError("Untranslated warning placeholder")
        values = {"build": GAME_RELEASE + " (Steam " + STEAM_BUILD + ")", "version": FRAMEWORK_VERSION}
        values.update(fields)
        if any(type(value) is not str or not value or len(value.encode("utf-8")) > 256
               or any(ord(char) < 32 for char in value) for value in values.values()):
            raise ValueError("Invalid warning value")
        rendered = selected[key]["text"].format(**values)
        if len(rendered.encode("utf-8")) > MAX_TEXT_BYTES:
            raise ValueError("Oversized warning result")
        return rendered
    except Exception:
        return WARNING_FALLBACKS[fallback_key]


def _message_box(title, message):
    import ctypes as C
    from ctypes import wintypes as W
    if os.name != "nt":
        return
    function = C.WinDLL("user32", use_last_error=True).MessageBoxW
    function.argtypes = [W.HWND, W.LPCWSTR, W.LPCWSTR, W.UINT]
    function.restype = C.c_int
    function(None, message, title, 0x10)  # MB_OK | MB_ICONERROR; host-only UI.


def show_failure(error, language=None, show_dialog=True):
    """Report outside NMS. Display failures never change the refusal decision."""
    if not isinstance(error, CompatibilityError):
        error = CompatibilityError("launcher.invalid_package")
    title = warning_text("launcher.blocked_title", language)
    message = warning_text(error.key, language, **error.fields)
    try:
        print(title + ": " + message, file=sys.stderr)
    except Exception:
        pass
    if show_dialog is True:
        try:
            _message_box(title, message)
        except Exception:
            pass
    return message
