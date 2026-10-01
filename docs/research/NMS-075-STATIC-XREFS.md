# Cosmos 7.05 static XREF record: teleport-related state

Status: recorded 1 October 2026 against the exact Steam Cosmos 7.05 executable used by the native 0.10.1 test candidate. This is a read-only reverse-engineering record. It contains derived addresses and counts, not game binaries, raw disassembly or personal machine paths.

## Purpose

The goal of this pass was to narrow the search for a successful local teleporter-completion event. The current release has no verified teleport-arrival trigger. Earlier source/API searches did not identify a trustworthy completion callback, so this pass searched the exact executable for RIP-relative references to teleport-related data and the `gcpersonalteleporter.cpp` marker.

## Executable and mapping assumptions

- Game release: **Cosmos 7.05**
- Steam build: **25624745**
- Required executable SHA-256: `671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`
- Image base used by the scan: `0x140000000`
- `.text` RVA/file start: `0x1000 / 0x400`
- `.text` scan size: `0x340E500`
- `.rdata` RVA/file start: `0x3410000 / 0x340EA00`

The target VA is derived as:

`RVA = RDATA_RVA + (target_file_offset - RDATA_FILE)`

`VA = IMAGE_BASE + RVA`

This mapping is only the address-conversion step; it does not prove that a target is code or that a reference is semantically related to teleport completion.

## Targets

| Target | File offset | Derived RVA | Derived VA |
|---|---:|---:|---:|
| `AngleFromBaseComputerWhenTeleporting` | `0x34D0888` | `0x34D1E88` | `0x1434D1E88` |
| `DistanceFromBaseComputerWhenTeleporting` | `0x34D08B0` | `0x34D1EB0` | `0x1434D1EB0` |
| `Teleporting` | `0x4AA4738` | `0x4AA5D38` | `0x144AA5D38` |
| `gcpersonalteleporter.cpp` | `0x4ADD330` | `0x4ADE930` | `0x144ADE930` |

## RIP-relative candidate references

The discovery scanner walked the `.text` byte range and recognized a five-byte RIP-relative form when the first byte treated as ModRM satisfied `(modrm & 0xC7) == 0x05`. It resolved the signed 32-bit displacement against the end of that ModRM-plus-displacement sequence. The original table below mislabeled the resulting ModRM-byte offsets as instruction starts; they are not instruction boundaries and must not be used as hook addresses.

This is a **candidate-reference scanner, not a disassembler**. A byte-pattern hit must be decoded in context before it can be called a real code XREF.

### `AngleFromBaseComputerWhenTeleporting`

4 candidate references:

| Candidate ModRM-byte VA | Candidate ModRM-byte RVA | Candidate file offset |
|---:|---:|---:|
| `0x140136014` | `0x136014` | `0x135414` |
| `0x14284924E` | `0x284924E` | `0x284864E` |
| `0x14285923A` | `0x285923A` | `0x285863A` |
| `0x142859261` | `0x2859261` | `0x2858661` |

### `DistanceFromBaseComputerWhenTeleporting`

4 candidate references:

| Candidate ModRM-byte VA | Candidate ModRM-byte RVA | Candidate file offset |
|---:|---:|---:|
| `0x1401360AF` | `0x1360AF` | `0x1354AF` |
| `0x142849264` | `0x2849264` | `0x2848664` |
| `0x14285929F` | `0x285929F` | `0x285869F` |
| `0x1428592C6` | `0x28592C6` | `0x28586C6` |

### `Teleporting`

1 candidate reference:

| Candidate ModRM-byte VA | Candidate ModRM-byte RVA | Candidate file offset |
|---:|---:|---:|
| `0x140AC41AA` | `0xAC41AA` | `0xAC35AA` |

### `gcpersonalteleporter.cpp`

1 candidate reference:

| Candidate ModRM-byte VA | Candidate ModRM-byte RVA | Candidate file offset |
|---:|---:|---:|
| `0x1414417A4` | `0x14417A4` | `0x1440BA4` |

## What this establishes

The exact 7.05 executable contains four byte-level RIP-relative candidate references to each of the two teleport-distance/angle labels, one candidate reference to `Teleporting`, and one to the `gcpersonalteleporter.cpp` marker. The candidate offsets above are useful search locations only; the instruction starts below were verified by disassembling from `.pdata` function boundaries.

## Decoded instruction-boundary verification

The follow-up used `tools/native_string_xrefs.py` with the exact executable
SHA-256 above, Python 3.11.9, `pefile 2024.8.26`, and `Capstone 5.0.9`. It
decoded 52,096,118 runtime-function bytes and skipped zero ranges. The verified
direct RIP-relative instruction starts and containing function ranges are:

| String target | Instruction RVA(s) | Containing function RVA(s) |
|---|---|---|
| `AngleFromBaseComputerWhenTeleporting` | `0x136012`, `0x284924C`, `0x2859238`, `0x285925F` | `0x131510-0x14AA8E`, `0x28484E0-0x284C64A`, `0x28560B0-0x286598C` |
| `DistanceFromBaseComputerWhenTeleporting` | `0x1360AD`, `0x2849262`, `0x285929D`, `0x28592C4` | `0x131510-0x14AA8E`, `0x28484E0-0x284C64A`, `0x28560B0-0x286598C` |
| `Teleporting` | `0xAC41A8` | `0xAC40FB-0xAC445B` |
| `gcpersonalteleporter.cpp` | `0x14417A2` | `0x1441770-0x144181D` |

Every raw ModRM-byte candidate above is two bytes after the verified start of
its corresponding `REX.W + LEA` instruction. This offset pattern is a property
of those encodings, not a general address correction rule. Always use the
decoded instruction and its `.pdata` owner. The `Teleporting` instruction
passes a string value into a shared helper; it does not expose a successful
local-arrival result. The source-file marker remains a diagnostic/source
location lead, not a function name or callback. Correcting these byte offsets
does not identify a teleport trigger.

It does **not** yet establish which candidate belongs to the actual successful local teleporter flow. In particular:

- The two `AngleFrom...` / `DistanceFrom...` targets have multiple references, so they are not unique identifiers of a completion callback.
- `Teleporting` has one candidate reference in the scan, which makes it a useful anchor for contextual decoding, but the hit alone is not a callback identification.
- `gcpersonalteleporter.cpp` is a source-file marker/name target and must not be treated as a function entry point.
- No teleport hook is being added, and the published 0.10.1 archive remains unchanged.

## Next analysis step

Walk the enclosing control flow from the verified instruction sites, then follow calls/branches around the state transition to determine whether a candidate is:

1. teleporter setup,
2. transient teleport-in-progress state,
3. arrival/completion,
4. cleanup/failure, or
5. unrelated data access.

For a viable completion candidate, verify that it fires only for the local player and only after successful teleport completion. Position changes, generic warp, system travel, menu transitions and network-client updates remain insufficient substitutes.

## Raw scan result retained

The source scan reported:

~~~text
AngleFromBaseComputerWhenTeleporting: file=0x34D0888 RVA=0x34D1E88 VA=0x1434D1E88
DistanceFromBaseComputerWhenTeleporting: file=0x34D08B0 RVA=0x34D1EB0 VA=0x1434D1EB0
Teleporting: file=0x4AA4738 RVA=0x4AA5D38 VA=0x144AA5D38
gcpersonalteleporter.cpp: file=0x4ADD330 RVA=0x4ADE930 VA=0x144ADE930

=== SEARCHING RIP-RELATIVE REFERENCES ===

--- AngleFromBaseComputerWhenTeleporting ---
count=4
instruction VA=0x140136014 RVA=0x136014 disp_file=0x135414
instruction VA=0x14284924E RVA=0x284924E disp_file=0x284864E
instruction VA=0x14285923A RVA=0x285923A disp_file=0x285863A
instruction VA=0x142859261 RVA=0x2859261 disp_file=0x2858661

--- DistanceFromBaseComputerWhenTeleporting ---
count=4
instruction VA=0x1401360AF RVA=0x1360AF disp_file=0x1354AF
instruction VA=0x142849264 RVA=0x2849264 disp_file=0x2848664
instruction VA=0x14285929F RVA=0x285929F disp_file=0x285869F
instruction VA=0x1428592C6 RVA=0x28586C6 disp_file=0x28586C6

--- Teleporting ---
count=1
instruction VA=0x140AC41AA RVA=0xAC41AA disp_file=0xAC35AA

--- gcpersonalteleporter.cpp ---
count=1
instruction VA=0x1414417A4 RVA=0x14417A4 disp_file=0x1440BA4

=== DONE ===
~~~

The scan itself is not committed to the repository. Only this sanitized result and methodology are retained here.
