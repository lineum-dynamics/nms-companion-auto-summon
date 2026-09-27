"""Build a candidate Win64 leaf filter; importing this module executes no code.

This is developer-only preparation, not a game installer or an enabled hook.
The entry must be reached directly from the audited native call site, where
RDI is the live menu. It never changes selection or inspects physical keys.
All other callers jump to the supplied original trampoline before reading RDI.

The direct reads require the caller's menu/vector lifetime. Bounds checks do
not validate memory ownership; owned-buffer tests cannot establish game safety.
"""

import struct


CUSTOM_ACTION_MARKER = b"CAS_MENU_V1\xA7\x19\x5C\xE3\x42"
GET_BUTTON_RVA = 0x2C1DDE0
BIND_QUERY_RETURN_RVA = 0x151DDEB
MAX_USER_ADDRESS = 0x7FFFFFFFFFFF


def _address(value):
    if type(value) is not int or not 0x10000 <= value <= MAX_USER_ADDRESS:
        raise ValueError("Expected a non-null x64 user address")
    return value


class _Code:
    """Small fixed-instruction emitter with resolved relative branch labels."""

    def __init__(self):
        self.data = bytearray()
        self.labels = {}
        self.fixups = []

    def emit(self, value):
        self.data.extend(bytes.fromhex(value))

    def imm64(self, value):
        self.data.extend(struct.pack("<Q", value))

    def branch(self, condition, target):
        self.emit(condition)
        self.fixups.append((len(self.data), target))
        self.data.extend(b"\0" * 4)

    def label(self, name):
        if name in self.labels:
            raise ValueError("Duplicate native code label")
        self.labels[name] = len(self.data)

    def finish(self):
        for offset, name in self.fixups:
            struct.pack_into("<i", self.data, offset, self.labels[name] - offset - 4)
        return bytes(self.data)


def build_filter(expected_return, original, marker=CUSTOM_ACTION_MARKER):
    """Return our original machine code, never bytes copied from the game.

    Win64 volatile RAX/R10/R11 and flags are scratch. Arguments, nonvolatile
    registers, XMM registers and RSP are preserved. There are no calls, stack
    allocations, shared cells, input-button constants or Python callbacks.
    A matched None action with the entire marker returns false. Everything
    else tail-jumps to the original trampoline with untouched arguments.
    """
    _address(expected_return)
    _address(original)
    if not isinstance(marker, bytes) or len(marker) != 16 or not any(marker):
        raise ValueError("Expected a nonempty 16-byte private marker")
    c = _Code()
    c.emit("48 B8")                           # mov rax, expected_return
    c.imm64(expected_return)
    c.emit("48 39 04 24")                     # cmp [rsp], rax
    c.branch("0F 85", "forward")              # jne forward; before reading RDI
    c.emit("48 85 FF")                        # test rdi, rdi
    c.branch("0F 84", "forward")
    c.emit("8B 87 50 A0 00 00")               # mov eax, [rdi + depth]
    c.emit("83 F8 02")                        # cmp eax, 2 (unsigned rejects <0)
    c.branch("0F 87", "forward")
    c.emit("44 8B 94 87 88 A0 00 00")         # mov r10d, [rdi + rax*4 + selection]
    c.emit("45 85 D2")                        # test r10d, r10d
    c.branch("0F 88", "forward")              # js forward
    c.emit("C1 E0 04")                        # shl eax, 4
    c.emit("4C 8D 9C 07 58 A0 00 00")         # lea r11, [rdi + rax + vectors]
    c.emit("41 83 3B 00")                     # cmp capacity, 0 (signed native field)
    c.branch("0F 8C", "forward")              # jl forward
    c.emit("41 8B 43 04 85 C0")               # mov eax, [r11 + count]; test eax
    c.branch("0F 88", "forward")              # native signed counts cannot be <0
    c.emit("41 3B 03")                        # cmp eax, [r11 + capacity]
    c.branch("0F 87", "forward")
    c.emit("41 39 C2")                        # cmp r10d, eax
    c.branch("0F 83", "forward")              # jae forward
    c.emit("4D 8B 5B 08")                     # mov r11, [r11 + data]
    c.emit("4D 85 DB")                        # test r11, r11
    c.branch("0F 84", "forward")
    c.emit("4D 69 D2 E0 00 00 00")            # imul r10, r10, item_size
    c.emit("4D 01 D3")                        # add r11, r10
    c.branch("0F 82", "forward")              # jc forward
    c.emit("41 83 7B 04 00")                  # cmp dword [r11 + action], None
    c.branch("0F 85", "forward")
    c.emit("48 B8")
    c.imm64(int.from_bytes(marker[:8], "little"))
    c.emit("49 39 83 88 00 00 00")            # cmp [r11 + action_id], rax
    c.branch("0F 85", "forward")
    c.emit("48 B8")
    c.imm64(int.from_bytes(marker[8:], "little"))
    c.emit("49 39 83 90 00 00 00")            # cmp [r11 + action_id + 8], rax
    c.branch("0F 85", "forward")
    c.emit("31 C0 C3")                        # xor eax, eax; ret
    c.label("forward")
    c.emit("48 B8")                           # mov rax, original trampoline
    c.imm64(original)
    c.emit("FF E0")                           # jmp rax, preserving return address
    return c.finish()
