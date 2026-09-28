# Portable 0.9.2 scan and bounded provenance review

Recorded on 28 September 2026. This is a targeted, read-only investigation of
the exact quarantined release, not a malware clearance or a complete security
audit. The reviewed ZIP and executable have not been changed or rebuilt to
alter scanner results. No provider was contacted and no game process was
inspected, modified, terminated or reinjected during this review.

## Scanner observations

The Nexus upload for mod 4579, file 49196, is quarantined. The primary
VirusTotal UI readback for the exact archive reported **3/60** detections:
Bkav (`W32.Malware.D93D1E61`), Elastic (`Malicious`, moderate confidence), and
Varist (`W64/MSIL_Tiny.AF.gen!Eldorado`).

- [Exact archive report](https://www.virustotal.com/gui/file/1507a92c86b4126e0bfb9131ec2df228fbac2d95d3e88529db0499bd3f3349fe/detection)
- [Exact owned executable report](https://www.virustotal.com/gui/file/a661a4eafbaa38c9c4951adc555f5bab9f39be2f638e860655ee66603c27f5c4/detection)

The executable's separate primary report showed **8/70** detections: Bkav,
Cynet (score 100), Elastic (moderate), Google (`Detected`), McAfee
(`Ti!A661A4EAFBAA`), SecureAge (`Malicious`), Trapmine
(`Suspicious.low.ml.score`), and Varist (`W64/MSIL_Tiny.AF.gen!Eldorado`).
This confirms that the project's own compiled launcher is flagged; it does
not identify the triggering instruction or establish whether the detection
is correct. Counts are observations at this time, not permanent report values.

## Confirmed local provenance

The bounded review ran at approximately 15:36–15:40 Europe/Prague using normal
tooling Python to read bytes, `pefile` for static PE metadata, and Windows
PowerShell/.NET `ReflectionOnlyLoad` for metadata without invoking methods.
No candidate executable or candidate Python interpreter was executed.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| `CompanionAutoSummon-0.9.2-test.zip` | 23,419,195 | `1507a92c86b4126e0bfb9131ec2df228fbac2d95d3e88529db0499bd3f3349fe` |
| `Companion Auto Summon.exe` | 93,696 | `a661a4eafbaa38c9c4951adc555f5bab9f39be2f638e860655ee66603c27f5c4` |
| `portable-manifest.json` | — | `c896680df14ac8aa40060526dd21f1fd25940e2603b9a5efbee2b466b2949891` |

These values match the retained build receipt
`build/validation/portable-092-build.json`. The ZIP contains exactly 1,245
entries: 1,243 declared payload files, the manifest and launcher. Every payload
matches its declared SHA256; the ZIP and retained `build/portable-092-r1`
directory match byte for byte. No additional or missing file was found.

The three packaged `app/` files match the reviewed repository source exactly:

| Packaged file | Corresponding source | SHA256 |
| --- | --- | --- |
| `app/portable_launcher.py` | `tools/portable_launcher.py` | `320ea18c96afd27f2a43e38181ce10404670880d29571118c8cb9bceec80a5ef` |
| `app/portable_host_support.py` | `tools/portable_host_support.py` | `a0cffb1c9b5c4980427be9809a4758245aa7ff8cc20ffeee77ce15cc76e0d05b` |
| `app/PortableLauncher.cs` | `launcher/PortableLauncher.cs` | `09eef8e16bd229b83c9de2eec83b5121959cdf569f116d8cbc69600c9dddfb71` |

The owned `runtime/sitecustomize.py` likewise matches source, SHA256
`146eecc3b2c70fe5763ffe13a75a5abf492be863ec57168b8140eee2e4706d8e`.
`runtime/runtime-lock.json` is semantically identical to the reviewed source
lock. Its raw bytes differ because the runtime builder deliberately serializes
the parsed JSON with `json.dumps(lock, indent=2)` and LF termination; this is
the documented builder operation, not an additional dependency.

The executable is an x64 GUI PE with CLR IL-only flag `0x1`, no certificate
table, and no native import-table entries reported by the static parser. Its
only assembly references are `mscorlib`, `System.Windows.Forms`, `System`,
`System.Web.Extensions`, `System.Core` and `System.Drawing`. Its only embedded
resource is `PortableLocales`; those resource bytes match the reviewed
fourteen catalogs serialized by the builder. Reflection-only inspection also
confirmed the exact manifest-digest constant and a 1,020-byte IL body for
`Package.Verify`. No unrelated assembly or resource was identified.

The retained builder invokes the existing Windows .NET Framework `csc.exe`
with `/target:winexe`, `/platform:x64`, `/optimize+`, the standard framework
references and the locale resource. The current source and retained compiled
artifact have the expected provenance markers. This inspection did **not**
independently prove equivalence of every compiled instruction to the source;
no IL disassembler was available in the bounded check and no replacement
binary was built.

## Execution and network paths reviewed

The owned C# launcher constructs only package-local Python process paths:
`runtime/pythonw.exe` for Start and `runtime/python.exe` for the read-only
check. Arguments use `-I -B`, the package-local bootstrap, and an optional
quoted game directory. The check adds `--check-only --no-dialog`. It does not
invoke a shell, request elevation, download dependencies or install startup
persistence. Its timeout termination applies only to the owned read-only
check child, not the game or live mod host.

The owned Python bootstrap verifies the distribution, selects the guarded
game installation, backs up saves and preferences, and stages the allowlisted
mod into a private session directory. The owned host helper opens only the
fixed `steam://rungameid/275850` URI on the launch path, searches for the
corresponding Steam child, and retains the existing actual-process and DLL
injection guard. Its dynamic source wrapper reads an absolute local script
path for Unicode-compatible initialization. No HTTP downloader, remote source
execution, credential collection, unrelated executable launch or external
data transmission was found in these owned bootstrap/launcher sources.
The Microsoft redistributable URL is displayed as repair guidance; this code
does not automatically download or run it.

This scope does not mean every bundled vendor module lacks network or process
capabilities. The mod intentionally includes a native hook/injection framework
and a general Python standard library. Their complete implementation and the
running system were not rescanned or exhaustively audited here.

## Unresolved boundary

The scan cause remains **unresolved**. Matching source, manifest and build
receipt establishes which authored package was inspected; it does not override
the scanner results. The report names, unsigned status, small managed launcher
and intentional injection framework are not evidence sufficient to label this
a false positive or to attribute the detections to any one of those features.

The current evidence identifies the flagged owned executable and finds no
unexpected packaged file or owned bootstrap behavior in this bounded review.
It does not certify the archive as safe. Preserve these exact bytes and reports
for any further investigation; do not rename, repack or rebuild merely to get
past the quarantine, disable protection, or advise testers to ignore it.

Local evidence: `work/portable-092-provenance-review.json`,
`work/portable-092-metadata-review.json`, and the build receipt above. Additional
primary-report behavior/contained-file findings may be appended separately
with their evidence and limits.
