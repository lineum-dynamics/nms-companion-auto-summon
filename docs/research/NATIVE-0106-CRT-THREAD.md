# CRT-aware initializer thread — 28 October 2026

The four fixed component probes completed their approved VirusTotal submissions.
All eight scanners that report Yogi on the complete 0.10.5 ASI returned
Undetected for every probe. Each probe instead has one Cynet ML label, including
the inert CRT-only baseline. This does not establish a universally clean probe
or isolate a private rule. Bootstrap/host inspection or component interactions
remain unresolved; unused-code retention/reachability limits still apply.

## Concrete first-party contract correction

The complete runtime is built with the multithreaded static Microsoft CRT
(`/MT`, libcmt). Its worker uses C++ runtime facilities including strings,
filesystem, exception handling and formatting, but was created using Win32
CreateThread. Microsoft's [multithreading guidance](https://learn.microsoft.com/en-us/cpp/parallel/multithreading-with-c-and-win32)
requires CRT-aware thread creation for this combination. The [CreateThread
documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread)
also describes possible CRT failure under low memory.

Change the internal callback to `unsigned __stdcall` and use `_beginthreadex`.
Keep the once-only Interlocked owner, process pin, ordinary creation flags 0,
closed parent handle, no-wait initialization, host/hash/profile checks and all
gameplay filters. Returning from the callback uses the CRT's documented thread
cleanup. The factory's zero return sets stopped status 3 before any worker runs.
No player setting, language string or meaning changes.

This is a documented API contract correction. No player R6016/crash or
low-memory termination has been reproduced, and no Yogi causal connection is
claimed. It is not removal of a safety check or random player-binary variation.

## Distinct candidate and owned controls

Use the new **0.10.6-native-test** Microsoft candidate mode. Frozen 0.10.3,
0.10.4 and 0.10.5 files/reports remain separate. Game target stays exact
Windows/Steam Cosmos 7.06 / build 25732212 / executable SHA-256
13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No game image or mapping changes and no previous game acceptance transfers.

The candidate CI builds in two directories, requires DLL byte identity, runs
the existing owned validation bundle and positive-control Defender custom scan.
Only the first build also compiles a separate fault-injected DLL. Its forced
include substitutes exactly the source factory call after original CRT
declarations; it returns zero without starting a worker. Eight concurrent
initializer calls must produce stopped/inert status 3, exactly one factory
attempt, and no retry on another call. The fault DLL is never a player payload
or an antivirus submission. Ordinary six host runs must still refuse foreign
hosts with status 2.

| Gate | State |
| --- | --- |
| Local Python syntax/dependency/locale checks | Preparation only |
| Microsoft compilation and two-directory DLL identity | NOT CHECKED until CI readback |
| Ordinary owned functional bundle | NOT CHECKED until CI readback |
| Forced factory-zero, single-owner control | NOT CHECKED until CI readback |
| Exact-file Defender custom scan with positive control | NOT CHECKED until CI readback |
| Multivendor comparison for the exact new ASI | NOT CHECKED |
| Exact-candidate NMS acceptance and Nexus availability | NOT CHECKED |

Run native-msvc-candidate.yml on the exact source commit. Its first command
uses `build_native_msvc_audit.py --release-candidate --startup-failure-fixture`;
the second excludes the fault fixture. Read actual receipts before promoting
any gate. No source/profile override, installation, save change or support
contact is part of this correction.
