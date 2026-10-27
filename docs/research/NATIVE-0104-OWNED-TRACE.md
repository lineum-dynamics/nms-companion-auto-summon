# Owned-host runtime attribution — 27 October 2026

Status: **owned-host runtime captures completed**, with the limits below.
Earlier static and functional checks did not exhaust available internal
analysis. Further independent analysis remains available. No support/vendor
message has been authorized or sent; the held review draft remains a
last-resort option.

## Question and controls

Can the exact frozen ASI's actual API calls be distinguished from its host and
instrumentation during DLL load, inspection and unsupported-host initialization?
Specifically inspect direct caller provenance, requested sleep intervals,
thread creation flags and current-process memory handles. This can investigate
public sandbox labels without claiming access to private antivirus rules.

Use an owned, Microsoft-compiled host on isolated Windows GitHub Actions,
first without instrumentation and then with a pinned Frida agent. Four modes:

1. Baseline without the ASI.
2. Load the unchanged ASI, including normal DLL/CRT initialization.
3. Load and correctly invoke CasInspectHost.
4. Load, inspect and correctly invoke InitializeASI; verify unsupported-host refusal.

Every mode contains identical, benign host controls: a 7 ms Sleep, one owned
scalar WriteProcessMemory using GetCurrentProcess, and a normal worker thread.
These must appear as host-originating calls in the trace. InitializeASI's
known worker creation is an additional module-origin positive control.
Plain/instrumented phase records must match, with normal exit and no reported
crash, no event overflow, required interception points and exact module load.
Only an entirely completed capture gets CAPTURES_COMPLETED; it is not a safety verdict.

## Frozen identities

| Input | Source | ASI SHA-256 |
| --- | --- | --- |
| 0.10.3-native-test | 852c5c55458c563a8564090dd31305864483edf3 | 6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652 |
| 0.10.4-native-test | 7fd4bc09a3185a214a808052da61f2223999619b | 765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa |

Reproduce at the original source prefix with the original pinned compiler and
--teleport-candidate-trial. Validate the exact hash before execution and after
each audit. The game target stays Windows/Steam Cosmos 7.06 / build25732212 /
SHA-256 13d5060d4efb9d2a6a6b1b349bc4257231056cc2a055df4bb15d816262cc3499.
No game image is loaded or changed, and no game acceptance is inferred.

## Tool identities and execution boundary

- Existing official LLVM-MinGW20260922 archive, SHA-256
  e3ad77d117a4bea19a7a3b333341824d79a5a371004a10e25b8504e7b3047666,
  reproduces the frozen modules. No candidate bytes are varied for a score.
- Signed installed Microsoft x64 cl builds only the diagnostic host. Record
  compiler version/hash/signature, source hash and actual host SHA-256.
- Python 3.11.9; Frida 17.24.3 official PyPI Windows x64 ABI3 wheel, SHA-256
  61f5a53b146e0e7755d6c2bfa5405e14fe2373818ae5d98105c4eeca3face7d1.
  pip requires this exact hash and a binary wheel, without dependencies.
- The controller refuses execution outside this repository's Windows CI and
  refuses any ASI outside the two frozen hashes or an unrecognized host hash/name.
  The C++ host independently checks its name and CI/repository identity.
- The child receives an allowlisted environment without CI credentials. Calls
  are logged as module basenames/RVAs/flags, without memory contents or paths.
- No tool is installed on the owner's PC. No game process, player data,
  antivirus preference, exclusion, protection bypass or binary upload is part
  of the job. A blocked input remains a failed/blocked test.

## Limits

Instrumentation changes the controlled process and timing. The final method
attributes direct return addresses only, without indirect call stacks;
unknown owners stay unknown. Forwarded exports sharing
an address are deduplicated; different wrapper points can produce multiple
observations. This is selected API coverage, not complete system-call or
network-packet coverage. An unsupported owned host does not exercise native
game hooks or establish what ran in a different sandbox. Zero observations
do not identify a private rule or demonstrate a confirmed false positive.

Primary method references:
[Frida API](https://frida.re/docs/javascript-api/) and
[pinned wheel metadata](https://pypi.org/project/frida/17.24.3/#files).

## Initial preparation verification

Local syntax checks passed for Python and JavaScript. A negative control
confirmed that running the controller on the owner's PC was refused before
input access or importing Frida. At preparation time, actual CI builds, plain
cases, instrumentation readiness and runtime captures were not checked. The
attempts and completed runtime readback below supersede that initial state.

### First method attempt

Run 40576805956 at controller 8cca0d9 reproduced both frozen modules, compiled
both owned hosts with signed Microsoft tools and installed the hash-verified
instrumentation wheel. Both jobs stopped at baseline before loading any ASI.
Plain and traced host phases matched, all three positive API controls appeared,
and detach reported normal process termination without a crash. The required
RtlExitUserProcess event was absent, however, so both reports remain TOOL_ERROR.
No candidate runtime behavior or zero-threat finding follows from that attempt.

The next controller observes exit independently through a held Windows process
handle with query/synchronize rights, waits for process termination and reads
the actual exit code. A normal zero exit remains mandatory. This avoids relying
on an in-process final-exit callback after the instrumentation session tears
down. Retain the first attempt; do not relabel it a successful capture.

### Second method attempt and lower-interference follow-up

Run 40577586888 at e503c29 completed all four candidate modes, plain and
instrumented, with zero OS exit codes and known host/module positive controls.
The candidate's observed direct API contribution in these modes was one
InitializeASI CreateThread call, caller RVA 0x140E, creation flags 0. Its worker
then reached the unsupported-host status 2. No game hooks were exercised.

The original completed baseline/load/inspect captures and all four plain
cases, but its instrumented initialize case timed out. That case remains
TOOL_ERROR. One full-backtrace timeout cannot be assigned to a source defect,
an antivirus rule or a benefit from the query guard; the guard's changed path
was not being exercised in this unsupported host. The failed controller did
not retain its partial stdout on the exception path, a diagnostic limitation.

The next agent uses the direct API return address and a module map populated
by load notifications, avoiding stack walking/live module enumeration inside
loader/thread callbacks. It removes the unnecessary final-exit interception;
the independent OS exit check remains mandatory. Entered and returned calls
are recorded separately, and partial stdout is retained on failed cases.
This is a less intrusive method with narrower attribution, not a silent
promotion of the incomplete full-backtrace result. It cannot attribute an
indirect system-library call to the ASI through an uncaptured stack.

Sixteen additional plain initialization repetitions per exact ASI precede the
traced cases, each requiring exit 0, status 2 and hooks inactive. This is a
bounded check for an ordinary startup failure independent of the probe; it
does not prove the absence of a rarer fault or identify an earlier timeout.

## Completed direct-caller readback

[Run 40579107862](https://github.com/lineum-dynamics/nms-companion-auto-summon/actions/runs/40579107862),
controller `fd532ac1e30a0f2249e49a70b4210f744b848ddf`: **both jobs succeeded**.
All input/post-run module hashes match the frozen ASIs. Both jobs use the
same Windows image 20261022.344.1 and signed cl 19.44.35229.0, compiler SHA-256
fe251ef50a1545b1b0835ee17b1e785459712b38d79e45b5c1d3d28970a36619.
The official Frida 17.24.3 wheel hash was required by pip and the runtime
version checked. Nothing was installed on the owner's PC.

For **each** exact ASI, all 16 additional plain initialization repetitions
returned exit 0/status 2. Baseline/load/inspect/initialize also completed both
plain and instrumented: eight matched phase-record pairs across the two
modules, with actual Windows exit 0, known host API controls and positive
observation of the target image and its initialization worker where expected.

| Mode | Direct selected ASI API observations, both inputs | Host outcome |
| --- | --- | --- |
| Baseline without ASI | None; target image absent as required | Exit0 |
| Load unchanged ASI | None | Exit0, completed load |
| Correct CasInspectHost | None | Exit0, unsupported-host status 4 |
| Correct InitializeASI | One successful CreateThread, caller RVA 0x140E, creation flags 0 | Exit0, unsupported-host status 2 |

Entered and returned selected direct ASI call counts agree. No selected direct
ASI Sleep, WriteProcessMemory, SuspendThread or process-creation call was
observed in these owned-host modes. Host controls account for the recorded
memory write and sleeps; additional initializer polling also belongs to the
host. Identical API wrappers can produce multiple observations per logical
call. The direct caller map has zero unknown owners in these captures.

The initial instrumented baseline already has ws2_32/dnsapi instrumentation
points before the ASI is loaded. Library presence in a sandbox is therefore
not evidence that the ASI initiated network communication. No packet-origin
conclusion is made; watched API capture is not full network coverage.

This new bounded runtime evidence was available without support contact.
It does not identify the proprietary detector rule, establish a confirmed
false positive, or validate active hooks in NMS. The host's hooks_active=false
field follows its guard/report contract; this is not an independent hook-table
or whole-image patch inspection. Calls delegated through system libraries
cannot be attributed via a stack that this lower-interference mode does not
collect. The earlier full-stack timeout remains unresolved; later successful
plain repetitions/direct captures do not prove its cause.

Sanitized durable results, exact receipt/tool digests and all incomplete
attempts are in [the runtime evidence](NATIVE-0104-OWNED-TRACE-EVIDENCE.json),
SHA-256 `4d15608c308c8b2d059f716d27765ec254d0cd51f829126bb890e29544e24b8f`.
Raw trace logs and binaries are not committed. The CI uploaded JSON only.

## Remaining independent scope

The available internal analysis is not declared exhausted. These captures
exercise unsupported-host startup, not the following independent gates:

- Dynamic API attribution while MinHook changes **owned fixture targets**.
  The existing ABI fixture passes functional checks, but tracing must account
  for MinHook suspending injected instrumentation threads. A passive or
  explicitly instrumented fixture method is needed before assigning a hang.
- The complete UAL-to-ASI load lifecycle in an owned host, including teardown
  and error paths. This is distinct from direct LoadLibraryEx/InitializeASI.
- Active game/runtime observations for the exact candidate. This requires
  separate authorized game-test conditions and does not follow from CI.
- The exact antivirus matching rule remains undisclosed. Runtime evidence
  can reveal real behavior defects, but cannot itself classify a private rule.

The next bounded internal question is the owned active-hook transition, with
a separate host baseline and without blindly attaching a thread-owning probe
to a stop-the-world hook operation. No new player source repair is inferred
from the current observations. The support draft remains unsent.

### Later independent gates

The owned active-hook source fixture and exact new-candidate UAL lifecycle
have now completed in the separate
[0.10.5 investigation](NATIVE-0105-MSVC-CANDIDATE.md). They retain their own
source/binary scope and controls; the original direct-call captures above
are not retroactively promoted to active-game or indirect-stack evidence.
