"""Offline preparation of native menu/HUD text; not a native runtime adapter.

This module is not imported by the game mod or included in a play-trial bundle.
Preparation reads validated authored catalogs. Rendering uses immutable owned
text only, with no file access, language detection, settings or native calls.
UTF-8 here is a candidate transport: byte correctness does not verify game glyphs.
"""

from dataclasses import dataclass
from types import MappingProxyType

from validate_locales import validated_catalogs


MENU_BYTES = 127  # Existing 128-byte caption storage reserves one byte for NUL.
HUD_BYTES = 511   # Existing 512-byte notice storage reserves one byte for NUL.
SETTING_LABEL_KEYS = MappingProxyType({
    "enabled": "menu.automation",
    "selection_mode": "menu.selection",
    "prefer_same_biome": "menu.biome",
    "planets": "menu.planets",
    "space_stations": "menu.space_stations",
    "nexus": "menu.space_anomaly",
    "rotate_companions": "menu.rotate_companions",
})


class TextError(ValueError):
    """An owned text/state value cannot be represented without losing meaning."""


class TextTooLong(TextError):
    """The complete UTF-8 message exceeds the payload bound."""


def encode_payload(text, limit):
    """Encode complete text, excluding NUL; never truncate or replace characters."""
    if type(limit) is not int or not 0 < limit <= HUD_BYTES:
        raise TextError("Invalid text payload bound")
    if type(text) is not str or not text.strip() or any(ord(char) < 32 or ord(char) == 127 for char in text):
        raise TextError("Text must be nonempty and contain no control characters")
    try:
        payload = text.encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise TextError("Invalid Unicode text") from error
    if len(payload) > limit:
        raise TextTooLong("Complete text exceeds its byte bound")
    return payload


def _boolean(value):
    if type(value) is not bool:
        raise TextError("Expected an owned Boolean state")
    return value


def _mode(value):
    if type(value) is not str or value not in ("last_manual", "random", "by_habitat"):
        raise TextError("Unknown companion selection mode")
    return value


@dataclass(frozen=True)
class MenuTextState:
    """Copied display state, with no persistence values or native identities."""

    desired: bool | str
    pending: bool = False
    settings_ok: bool = True
    stopped: bool = False

    def __post_init__(self):
        for value in (self.pending, self.settings_ok, self.stopped):
            _boolean(value)
        if type(self.desired) is not bool:
            _mode(self.desired)


@dataclass(frozen=True)
class PreparedMessage:
    """Complete bytes and effective locale; fallback never claims translation."""

    text: str
    payload: bytes
    locale: str
    fallback_reason: str | None = None


class NativeText:
    """Prepare once offline, then render without I/O or mutable catalog aliases."""

    def __init__(self, *, locales_dir=None, source_root=None):
        catalogs = validated_catalogs(locales_dir, source_root)
        self._catalogs = MappingProxyType({
            locale: MappingProxyType({key: entry["text"] for key, entry in catalog["messages"].items()})
            for locale, catalog in catalogs.items()
        })

    @property
    def locales(self):
        return tuple(self._catalogs)

    def _render(self, locale, limit, compose):
        # Exact catalog IDs only. This is not an OS/game language resolver.
        recognized = type(locale) is str and locale in self._catalogs
        selected = locale if recognized else "en"
        reason = None if recognized else "unsupported_locale"
        text = compose(self._catalogs[selected])
        try:
            payload = encode_payload(text, limit)
        except TextTooLong:
            if selected == "en":
                raise
            selected, reason = "en", "byte_limit"
            text = compose(self._catalogs[selected])
            payload = encode_payload(text, limit)
        return PreparedMessage(text, payload, selected, reason)

    def parent(self, locale="en"):
        return self._render(locale, MENU_BYTES, lambda text: text["menu.parent_title"])

    def setting(self, key, state, locale="en"):
        if type(key) is not str or key not in SETTING_LABEL_KEYS:
            raise TextError("Unknown native setting key")
        if state is not None and type(state) is not MenuTextState:
            raise TextError("Expected copied menu text state")
        if state is not None and not state.stopped:
            _mode(state.desired) if key == "selection_mode" else _boolean(state.desired)

        def compose(text):
            if state is None:
                value = text["status.unavailable"]
            elif state.stopped:
                value = text["status.stopped"]
            elif key == "selection_mode":
                value = text[{"last_manual": "value.last_selected", "random": "value.random",
                              "by_habitat": "value.by_habitat"}[state.desired]]
            else:
                value = text["value.on" if state.desired else "value.off"]
            label = text["format.setting"].format(label=text[SETTING_LABEL_KEYS[key]], value=value)
            if state is not None and not state.stopped:
                if state.pending:
                    label = text["format.with_status"].format(label=label, status=text["status.pending"])
                elif not state.settings_ok:
                    label = text["format.with_status"].format(label=label, status=text["status.session_only"])
            return label

        return self._render(locale, MENU_BYTES, compose)

    def settings_notice(self, *, enabled, saved, enabled_changed, locale="en"):
        for value in (enabled, saved, enabled_changed):
            _boolean(value)

        def compose(text):
            fields = {"suffix": "" if saved else text["hud.session_suffix"]}
            if enabled_changed:
                fields["state"] = text["value.on" if enabled else "value.off"]
            return text["hud.automation_state" if enabled_changed else "hud.settings_updated"].format(**fields)

        return self._render(locale, HUD_BYTES, compose)

    def companion_notice(self, *, saved, enabled, selection_mode, locale="en"):
        _boolean(saved)
        _boolean(enabled)
        _mode(selection_mode)

        def compose(text):
            prefix = text["hud.companion_saved" if saved else "hud.companion_session"]
            if not enabled:
                return prefix + text["hud.auto_off_suffix"]
            if selection_mode == "random":
                return prefix + text["hud.random_on_suffix"]
            if selection_mode == "by_habitat":
                return prefix + text["hud.habitat_on_suffix"]
            return prefix

        return self._render(locale, HUD_BYTES, compose)

    def no_suitable_habitat_notice(self, locale="en"):
        """Compose evidence supplied by the caller; never decide eligibility."""
        return self._render(locale, HUD_BYTES, lambda text: text["hud.no_suitable_habitat"])
