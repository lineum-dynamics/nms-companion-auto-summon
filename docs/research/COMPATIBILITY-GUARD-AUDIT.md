# Compatibility guard audit

## Follow-up implementation: candidate 0.8.4

The historical gaps numbered 1 and 3 below are now addressed in source. Both
maintained Python hosts preflight the chosen game and the actual process is
rechecked before every DLL injection. The wrapper uses the existing target
handle with Unicode `QueryFullProcessImageNameW`, rehashes its image file and
requires equality with the selected path. It never substitutes a name/PID
search, caches a numeric handle or changes the original injector's return
address checks. Foreign `pymhflib` entries are rejected. Standalone package
validation additionally refuses missing/changed sibling files and unreviewed
TOML fields such as `required_assemblies` or suspended startup.

Gap 2 now has a scoped implementation: nine translated compatibility warnings
outside the game, selected from Windows UI language or an explicit override.
PowerShell and Python preserve console text and can show a host dialog; check-only
and explicit no-dialog modes suppress it. Malformed/stale catalogs retain
refusal and use emergency English package-failure text. Other launcher messages
and the final portable interface are not claimed complete. No native HUD route
is used, and none of the warning tests opens a real dialog.

Build/profile validation compares the host constants, JSON, manifest, native
and generated production mappings/framework pin, menu/filter and prototype
target. It parses source as data and refuses drift before creating outputs.
The native class/discovery latch remains in place; ordinary callback stopping
still does not mean native hooks have been unregistered.

Static inspection of installed pyMHF 0.2.4 confirms that this distinct
CompatibilityError propagates before its later game-termination cleanup block;
it is not one of the process-not-found errors that trigger another launch.
Both DLL loads in pyrun_injected pass the already-open actual process handle.
The wrapper does not kill, resume or relaunch a refused target. Live injection
of this candidate remains untested. The disk hash is not a complete audit of
the mapped executable, and saved custom technologies still need the separate
update/removal verification described in historical gap 5.

Final offline validation passed 329 production and 633 developer tests without
skips, including 19 actual PowerShell cases. Real Windows PowerShell 5.1 and
Python check-only invocations both accepted the current selected installation
and runtime. The former now avoids native argument double-quote stripping;
target path lengths are validated as UTF-16 units. The 40-file combined folder
also passed real-framework discovery and temporary preference exercises with
no native hooks or game connection. These do not establish a new live launch.

The API contract is documented by
[Microsoft: QueryFullProcessImageNameW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew).

## Historical audit before this implementation

Reviewed on 28 September 2026 against production 0.4.7 and prepared combined
trial 0.8.3, plus the installed pyMHF 0.2.4 source. This was a read-only source
audit: no game/process inspection, injection, hook registration or deployment.
The running installation was not changed.

## Existing protection

- The supported PowerShell entry validates package checksums, the pinned
  framework and the exact executable SHA before dependency setup or host
  launch. A mismatch produces an English error and refuses launch. It hashes
  the executable again after setup. Process-enumeration errors fail closed;
  `-CheckOnly` makes no setup changes and may run while NMS is open.
  References: `Start-CompanionAutoSummon.ps1:16`, `:130`, `:139`, `:156`,
  `:187`, `:198`.
- The combined Python host also validates its complete payload/discovery set,
  pyMHF version, explicit game executable and closed-game state before asset
  staging and `run_module`. Installing its DLL-address wrapper merely defines
  the wrapper; it does not inject at that point.
  References: `tools/Launch-CompanionAutoSummon-PlayTrial.py:44`, `:169`, `:191`.
- Production's import-time `supported_runtime()` requires an injected context,
  positive base, pyMHF 0.2.4 and the exact executable SHA. The class receives
  `_disabled = True` on mismatch or covered read/metadata errors; an external
  log records the refusal. The menu independently checks the same SHA,
  framework and x64 pointer size, with its source flag disabled by default.
  References: `src/runtime.py:84`, `:169`, `:1291`;
  `tools/quick_menu_order_trial.py:76`, `:233`, `:262`.
- This class flag is early enough in the supported framework. In pyMHF 0.2.4,
  `core/mod_loader.py:69` excludes disabled classes during discovery;
  `:391` preloads only those discovered classes; `:539` instantiates and then
  registers callbacks; `:535` initializes native hooks. The static wrappers
  defined earlier in the mod only create metadata: `core/hooking.py:926`,
  `:1044`, `:1125`. Native wrapper resolution/calls occur in `:960`, not in the
  decorator constructor. A class rejected by normal discovery therefore does
  not register this mod's native hooks, even when loaded outside our launcher.
- Before its independent native binding filter is installed, the menu guard
  additionally checks the actual current process path/base, framework versions,
  disk SHA and original target bytes. Before custom operations it validates
  its pinned installation, relay, full verified 19-byte trampoline and filter.
  References: `tools/quick_menu_guard_runtime.py:88`, `:190`, `:254`, `:263`,
  `:313`, `:381`. This is targeted integrity checking, not validation of every
  native RVA or of the full mapped executable.

The manifest, generated production file and all three source SHA constants
matched in this audit. Existing guard tests cover wrong framework, unreadable
or wrong executable, non-injected context and disabled initialization
(`tests/test_runtime.py:134`; `tools/tests/test_quick_menu_order_trial.py:136`).
They do not establish that an arbitrary future game build is safe to run with
the framework injected.

## Remaining gaps and limits

1. **The direct standalone Python host has no pre-injection game validation.**
   `Launch-CompanionAutoSummon.py:155` checks the mod filename, takes a host
   lease and invokes pyMHF. Its DLL-address guard validates injected DLL
   identity, not NMS compatibility. The later production class guard still
   prevents our native hooks, but pyMHF may already have injected. Therefore
   “a mismatched game never receives injection” is true only of the checked
   launch path, not of every exposed entry point.
2. **The final player-facing mismatch experience is unfinished.** PowerShell
   has an English console error; direct runtime refusal is logged, and the
   menu class has no separate mismatch notice. There is no guaranteed visible,
   maintained localized warning across entry points. The current locale
   catalogs do not cover launcher messages (`LOCALIZATION.md`).
3. **Builds do not centrally enforce agreement between all compatibility
   declarations.** `build.py:30` concatenates source; the combined builder
   checks production/framework versions but copies the manifest's game SHA
   (`tools/build_quick_menu_play_trial.py:224`). Packaging verifies tested
   source hashes and framework reports (`tools/package.py:42`) rather than
   explicitly comparing every game-SHA declaration. They agree now; future
   drift could pass launcher preflight and leave one or both Mods disabled.
4. **A callback safety latch is not a pre-registration version guard.**
   Production `_fail_closed()` stops its behavior, and menu `_stop()` stops
   custom work, but neither unregisters every framework hook. Menu
   initialization failure also leaves the instance stopped rather than
   removing its collected hook metadata. Keep executable rejection in the
   class/discovery gate; do not replace it with an `enabled`/`_stopped` check
   inside callbacks. An already installed binding filter intentionally remains
   pinned until process exit to protect existing custom entries.
   References: `src/runtime.py:703`; `tools/quick_menu_order_trial.py:270`,
   `:294`; pyMHF `core/mod_loader.py:539`.
5. **Runtime disable cannot establish saved-technology compatibility.** Current
   loose icon textures and runtime menu entries do not prove future custom
   technology IDs remain safe after an update or removal. Such persistence
   needs its own verified migration/removal contract before live use. No
   technology inventory is granted or modified by this audit.

## Recommended next gate

Use one host-side compatibility preflight for every maintained launch entry,
before framework injection, asset staging or native registration. Reject
unknown/unreadable builds without an override; retain the independent
import-time class guards as a second check. Add an offline build assertion
that manifest, generated production and menu/filter constants agree.

Present one clear localized launcher result identifying the supported build,
that the mod was not activated, and that NMS can be started normally without
it. Extend English and all affected catalogs/validator coverage in the same
change. Do not kill the game, automatically load a save, or silently rewrite
preferences. The present refusal leaves the normal Steam launch route
available; it does not itself launch vanilla NMS or prove all framework/game
failure modes are recoverable.

Never call the in-game HUD to announce an unsupported build: the HUD reads
fixed layout offsets and calls an exact-build native function
(`src/runtime.py:158`, `:607`). Its text-only fallback still uses that same
native route. A compatibility warning must stay outside the game's native
integration until compatibility has been established.

No player-facing text or behavior changed in this audit; locale data therefore
needed no update.
