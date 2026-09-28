# Portable 0.9.2 launcher: complete offline build equivalence

Recorded on 28 September 2026 against repository commit
`845f6ffd69f83a69d470eb7ed09e73000c797435`, branch
`feat/portable-multiplayer-trial`. This extends the bounded provenance check in
[PORTABLE-SCAN-092.md](PORTABLE-SCAN-092.md). It does not clear the scanner result
or resolve the Nexus quarantine.

## Result

The exact flagged launcher is byte-for-byte identical to one faithful rebuild
except for the compiler-generated COFF timestamp and module identifier (MVID).
Every managed instruction, metadata table, embedded resource, native resource,
remaining PE header byte and padding byte matches. A separate reflection-only
inventory confirms that all 28 method/constructor bodies and their associated
metadata match.

This closes the earlier gap concerning comparison of the complete compiled
launcher with its retained source and builder. No additional payload absent
from that build was found in the flagged executable. It does **not** establish
that every source behavior or bundled dependency is safe, explain the antivirus
heuristics, or authorize ignoring quarantine.

The retained release was not changed. Exactly one offline comparison build was
made; neither executable was launched, uploaded or submitted to a scanner.
The rebuild is a research artifact, not a replacement release or scan variant.
No game process, runtime, save, antivirus setting or execution policy was
changed. No provider or person was contacted.

## Inputs and compiler

| Input | SHA256 |
| --- | --- |
| Retained `build/portable-092-r1/Companion Auto Summon.exe` | `a661a4eafbaa38c9c4951adc555f5bab9f39be2f638e860655ee66603c27f5c4` |
| Same release's `portable-manifest.json` | `c896680df14ac8aa40060526dd21f1fd25940e2603b9a5efbee2b466b2949891` |
| Faithful rebuild under `work/launcher-il-audit-092/rebuilt/` | `0fbdfe07d3d2fc62b1161a886036c4a5173f35d45c7656d0aaa2c0f27fffefc0` |
| Existing Windows .NET Framework compiler | `46809206887326d2d24db1eff1f3064de972c3451abe766b49111450a5e08e00` |

Both launcher files are 93,696 bytes. The unchanged
`tools/build_portable_entrypoint.py` read the same source, validated language
catalogs and retained manifest, and compiled one fresh output. The exact command
was:

```text
python -X utf8 -B tools/build_portable_entrypoint.py --manifest build/portable-092-r1/portable-manifest.json --output work/launcher-il-audit-092/rebuilt/CompanionAutoSummon.exe
```

The builder used
`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`, 2,569,832 bytes,
product version `4.8.9221.0`, file version
`4.8.9221.0 built by: NET481REL1LAST_25H2`. Windows
`Get-AuthenticodeSignature` reported **Valid / Signature verified** for that
compiler. Its signer is `Microsoft Windows, Microsoft Corporation`; its
certificate thumbprint is `BAC13DF18B37E808208A39D3A54CCE975FAC8C1D`. A Microsoft
Time-Stamp Service countersignature is present. This signature authenticates
the compiler, not the unsigned generated launcher.

The compiler configuration specifies CLR v4.0.30319. Its default `csc.rsp`
contains normal framework `/r:` references; no repository-root `csc.rsp` was
present. Their SHA256 values were recorded as
`2d4610ade011e530d817dd3ba4fc787e5dc0c2297cc520c30a643b8fb13f9093`
and `e2021640c1f8ad500549fc89cd53bc4c2f0fa13fee9034714142d93c5d554042`
respectively. This was not a full Windows installation or compiler toolchain
forensics audit.

## Full PE comparison

A small owned parser read PE32+ headers, section mappings, the CLR header and
metadata stream directory directly from bytes. It compared the entire files.
Only 18 bytes differ, in these two generated fields:

| Field | File offset | Field length | Retained | Rebuilt |
| --- | ---: | ---: | --- | --- |
| COFF `TimeDateStamp` | 136 | 4 | `1790601755` | `1790603278` |
| Sole `#GUID` heap / module MVID | 89,952 | 16 | `d9936665-dbf0-4a9f-8bb4-1451f4a9d55e` | `3b903adc-3caf-422e-b10a-c699ec4d39fb` |

Two bytes of the four-byte timestamp differ; all sixteen GUID bytes differ.
The `#GUID` heap is exactly sixteen bytes in both files, and reflection-only
inspection independently identifies those bytes as their respective MVIDs.
After replacing only these two fields with zeroes in **in-memory comparison
buffers**, both complete buffers have SHA256
`be959ade8bb1703254b1c76d32a34345f5e0a26459c3a6784e0211bde1751308`.
Neither file on disk was normalized or modified.

The PE has only `.text` and `.rsrc` sections. CLR flags are `ILONLY` (`0x1`),
entry-point token is `0x06000012`, native import directory is empty, certificate
directory is empty, and PE checksum is zero. All these values agree between
the files. The unchanged end of the second section coincides with file end;
there is no additional overlay. The metadata streams `#~`, `#Strings`, `#US`
and `#Blob` are identical in their entirety.

## Independent managed inventory

Windows PowerShell's .NET Framework `ReflectionOnlyLoad(byte[])` inspected each
file in a separate process. Candidate methods, constructors, static
initializers and attribute constructors were not invoked. The initial attempt
to run an owned `.ps1` via `-File` was refused by the existing script policy;
the same owned inspection statements were subsequently supplied as a direct
Windows PowerShell command. Policy and protection settings were unchanged.
PowerShell Core cannot perform this reflection-only inspection, so the
Windows PowerShell executable was selected explicitly.

The serialized inventory includes type names/tokens/attributes, every declared
method and constructor's raw IL and SHA256, signatures, implementation flags,
local-variable signatures, maximum stacks, exception clauses, fields and
literal values. It also includes the entry point, complete assembly references
and embedded-resource digests. Apart from paths, file hashes and MVID, both
inventories are identical.

| Managed component | Methods / constructors |
| --- | ---: |
| `Package` | 5 |
| `Texts` | 2 |
| `LauncherWindow` | 10 |
| `Program` | 1 |
| Five compiler-generated closure / async types | 10 |
| **Total: 9 types, 5,161 IL bytes** | **28** |

There are zero P/Invoke declarations. The six assembly references are
`mscorlib`, `System.Windows.Forms`, `System`, `System.Web.Extensions`,
`System.Core` and `System.Drawing`. The only managed resource is
`PortableLocales`, 73,865 bytes, SHA256
`46cdd708f4f439aea3782dcbeede77f1efd1452d535158d06be714b935e0798f`.
The manifest-digest constant matches the retained manifest hash above.

The generated assembly identity is
`CompanionAutoSummon, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null`.
The build has no publisher Authenticode signature or explicit assembly version
metadata. These are verifiable packaging facts; this audit does not infer that
either fact caused a scanner detection or that adding them would clear it.

## Evidence and remaining boundary

Local, non-distributed evidence is retained under
`work/launcher-il-audit-092/`:

- `compare_pe.py` and `pe-equivalence.json`: complete byte comparison and
  independently located generated fields.
- `read_managed_metadata.ps1`, `original-managed-metadata.json` and
  `rebuilt-managed-metadata.json`: reflection-only method inventories.
- `managed-equivalence.json`: equality receipt and individual method hashes.
- `compiler-provenance.json`: compiler path, hash, signature and configuration.
- `rebuilt/CompanionAutoSummon.exe`: the sole faithful comparison build.

This gives strong reproducibility evidence for the **owned launcher**. It is
not an independent source-code security proof, malware classification, or a
complete audit of the bundled Python and intentional native injection
framework. In particular it cannot explain why eight antivirus engines flagged
this authored executable. The quarantined archive and launcher hashes in
[PORTABLE-SCAN-092.md](PORTABLE-SCAN-092.md) remain the release identities under
investigation; a rebuild with a different timestamp or MVID is not a remedy.

There is no localization impact: the audit changes no player-facing text,
behavior, source, build configuration or compatibility claim.
