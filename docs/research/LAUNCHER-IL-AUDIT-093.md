# Portable 0.9.3: independent build from shipped review inputs

Recorded on 28 September 2026. This is an offline reproducibility check of the
frozen `build/portable-093-r1` launcher, extending
[the 0.9.2 audit](LAUNCHER-IL-AUDIT-092.md). It is not a scanner clearance or a
claim that Nexus has accepted the archive.

## Result

**The shipped reviewer recipe is sufficient.** One independent compilation
using only the package's supplied build inputs reproduced every launcher byte
except the independently identified compiler timestamp and module identifier
(MVID). No missing compiled input or other mismatch was found.

The comparison build was not run, uploaded or scanned. The original candidate,
running game, runtime, saves and security settings were not modified. No Git
operation or external communication occurred. Only one comparison executable
was built; it is retained as evidence, not a proposed replacement release.

## Exact inputs

The `app/BUILD-LAUNCHER.txt` PowerShell recipe was followed with its output
directory relocated from a fresh temporary directory to fresh
`work/launcher-il-audit-093/rebuilt/`. Compiler options, output filename and
all compiled inputs were unchanged. The only source substitution was the
SHA256 of the supplied root manifest. The repository's Python builder was not
used to produce this independent comparison executable.

| Artifact | SHA256 |
| --- | --- |
| Supplied `Companion Auto Summon.exe`, 94,720 bytes | `0df7e0930c407ecdb64eba6c79ff7bae535606d9d71932e8342926e6b6120172` |
| Supplied `portable-manifest.json` | `eecf4602887a189d94558ca5335cfa6d2173ee479747e5fa4366cbdfb20a2078` |
| Independent `CompanionAutoSummon.exe`, 94,720 bytes | `5454212489f710dc4fb353c4d5bb61cc60de8c165baeb6bd452df55c26f204a9` |

All supplied compiler inputs and the recipe matched their payload manifest
hashes:

| Supplied file | SHA256 |
| --- | --- |
| `app/PortableLauncher.cs` | `09eef8e16bd229b83c9de2eec83b5121959cdf569f116d8cbc69600c9dddfb71` |
| `app/AssemblyInfo.cs` | `12608cd799ed31dd47554d7ad6b5b61f53457c4a97175567900c0a7bb9980179` |
| `app/PortableLauncher.manifest` | `571e11b4fafd545723bf2fdc812ad0432159498f5e2190a12302351d0a66bab5` |
| `app/portable-locales.json` | `46cdd708f4f439aea3782dcbeede77f1efd1452d535158d06be714b935e0798f` |
| `app/BUILD-LAUNCHER.txt` | `170ff3a9ec27bd4b8edf8f16c672f77deeaec883e71cea7ffaaa92c353fade91` |

The C# source contains exactly one manifest-digest placeholder, and the
packaged application manifest has its version already resolved. The recipe
compiles that resolved `asInvoker`, `uiAccess=false` manifest directly.

The existing Windows .NET Framework compiler was
`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`, version 4.8.9221.0.
Its SHA256 remained
`46809206887326d2d24db1eff1f3064de972c3451abe766b49111450a5e08e00`, and its
Microsoft Authenticode signature was again reported **Valid**. No compiler or
other tool was installed.

## Complete comparison

Direct PE parsing located the COFF timestamp and CLR metadata streams in both
files. Exactly seventeen bytes differ:

- One byte inside the four-byte timestamp at file offset 136. Timestamp values
  are `1790604058` and `1790604136`.
- Sixteen bytes in the sole sixteen-byte `#GUID` heap at file offset 90,268.
  Reflection-only inspection independently identifies their MVIDs as
  `c708daef-642b-44aa-8d60-e50685f604c2` and
  `f69b4b19-a81c-4775-8294-71fa3be19e9d`.

Every other byte is identical, including all IL, metadata, embedded locales,
Windows manifest, version resources, section padding and PE headers. Zeroing
only those two generated fields in temporary **in-memory comparison buffers**
gives the same complete-buffer SHA256:
`b354e4058643c1ddb56d3e57fa8a4d2358cd04fe5185fd31129431b80bed5a96`.
No candidate file on disk was normalized or changed.

The separate Windows PowerShell `ReflectionOnlyLoad` inventories contain nine
managed types and 28 method/constructor bodies totaling 5,161 IL bytes, with
zero P/Invoke declarations. Raw instructions, method signatures and flags,
locals, exception handlers, fields, constants, assembly references and resource
digests match after excluding only source path, file hash and MVID. Neither
assembly's methods, constructors nor attribute constructors were invoked.

The assembly version is now `0.9.3.0`. Windows file metadata identifies
`Lineum Dynamics`, `Companion Auto Summon for No Man's Sky`, file version
`0.9.3.0` and product version `0.9.3-test`. The actual locale resource still
matches the exact shipped `app/portable-locales.json` bytes. These improvements
make the package easier to inspect; they are not evidence of scanner approval.

## Retained evidence and limits

`work/launcher-il-audit-093/` contains the independent rebuilt executable,
`compare_pe.py`, `pe-equivalence.json`, both full managed metadata inventories,
`shipped-input-audit.json` and `file-identity.json`. Reflection inspection reused
the owned helper retained with the 0.9.2 evidence.

This check establishes complete build equivalence on this verified compiler
and that the distributed reviewer inputs are sufficient. It does not guarantee
the same output with a different compiler version, audit all Python/vendor
behavior, establish multiplayer compatibility, or predict Nexus/antivirus
results. A provider's actual scan result must be recorded separately.

There is no localization impact: this audit changes no player-facing text or
runtime behavior.
