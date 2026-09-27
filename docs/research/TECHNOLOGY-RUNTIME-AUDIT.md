# Rechargeable technology: runtime audit

Status: **static research only**, 28 September 2026. No inventory observer,
charge consumption, recharge hook or installed-technology requirement has been
implemented by this audit. No game process or save was opened or modified.

## Result

The exact executable provides a credible, bounded route to read the player's
inventory stores. It does **not yet provide a verified callable API for charging
or discharging our technology**. A unique data-table technology and its recipe
can be prepared separately; `Chargeable` metadata alone does not connect it to
Companion Auto Summon or implement an energy transaction.

Do not use `cGcInventoryStore::Remove` as a charge debit. Its current technology
branch erases the inventory element rather than lowering its charge. Do not
write the apparent `Amount` field directly: that would bypass unknown native
notifications, charge rules, persistence and inventory bookkeeping.

## Evidence boundary

The installed Steam Cosmos 7.04 / build 25442159 executable was read as an
ordinary file and checked against SHA-256
`b7913f268dfc62386b6b68f524bfc8ade4a44a9f4fbad39085b7bf51be3680cb`.
Existing private `cas-quick-menu/native-audit/audit.py` signature matching and
the already available pefile/Capstone libraries supplied static evidence.
Raw disassembly and copyrighted binary data remain outside this repository.

The retained NMS.py source is commit
`b41bf9e6fdff1c833b77d805bb0c8da555c4ced4` (15 September 2026). Its names and
patterns are discovery aids, not an independently complete current ABI.
The retained ReNMS source targets Fractal 4.13; the retained NoMansSky.Api source
is from 2023. Neither establishes Cosmos compatibility.

## Exact-build observations

All addresses below are RVAs for the hash above, not absolute addresses.

| Observation | Static evidence | Scope |
| --- | --- | --- |
| Local player-state accessor | `0x2D79D0` reads application global `0x6E7AAE8` and returns application + `0xE70` | Corroborates the existing persistence audit; no null or lifetime protection is supplied by the accessor itself. |
| Inventory manager placement | Player-state constructor `0x56E960` calls `0x548B50` with state + `0x900` and the state pointer | The manager stores its owning state pointer at offset zero. |
| General inventory array | Manager constructor `0x548B50` constructs 33 stores beginning at manager + `0x10`, with stride `0x248` | Thus the first store is state + `0x910`; specialized ship/vehicle routes also exist. |
| Native inventory resolver | `0x47BDB0` accepts manager, inventory choice and optional secondary index; its general branch returns manager + `0x10` + choice * `0x248` | Other choices resolve elsewhere. This is an observed resolver, not an authorized call adapter. |
| Element lookup | Signature uniquely matches `GetElement` at `0x4C35B0`; it reads count at store + `0x8C`, data at + `0x90`, walks `0x30`-byte entries and compares the index at entry + `0x10` | Returns an element pointer or null. This confirms those layout facts, not concurrent-read safety. |
| Inventory initialization | Constructor uniquely matches `0x4CA2A0`; it clears vector storage beginning at + `0x88` | A bounded reader still needs to validate vector capacity/count and a stable read context. |
| Item removal | `Remove` uniquely matches `0x4CEAB0`, with a by-value index and amount override | Reads entry type at + `0x24`. Types 0/2 use amount at + `0x18`; type 1 takes the technology path and reaches vector erasure. It is not a technology charge API. |
| Packaging caller | `PackageTechnology` uniquely matches `0x5806B0`; it uses state + `0x900`, resolver `0x47BDB0`, then `GetElement` | Corroborates the resolver-to-element chain, but packaging mutates inventory and is not needed for this integration. |

Additional unique historical-pattern matches were found at `Add: 0x4CE130`,
`GetStatValue: 0x5A3D00` and `SaveToData: 0x5773C0`. A pattern match does not
verify a full signature, caller requirements or permission to invoke a function.
No recharge/debit function mapping was found in the retained SDK function table.

NMS.py labels inventory choice 1 as `Suit_Tech`. The current general resolver
would place that store at state + `0xB58` (application + `0x19C8`). The arithmetic
is verified; the semantic choice-to-exosuit-technology mapping still needs a
current native caller or controlled read-only observation before live use.

## Schema and historical-layout caution

The current MBINCompiler `GcInventoryElement` schema describes an ID, index,
amount, damage, maximum amount, type and installation flags. It is useful for
planning copied snapshots, but a serialized-schema definition alone does not
establish every live field's meaning or ABI. The exact lookup above independently
confirms the `0x30` stride and index + `0x10`; removal confirms amount + `0x18`
and type + `0x24` in that operation.

The retained MBINCompiler 4.12.1 definition instead starts with Type, puts ID at
+`0x08` and Index at +`0x28`. Do not reuse that old structure. Full installation,
damage, maximum charge and ID semantics must be checked against current code
before they gate automation.

Relevant author-maintained source references:

- [NMS.py runtime types at the retained commit](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py).
- [MBINCompiler technology schema](https://github.com/monkeyman192/MBINCompiler/blob/development/libMBIN/Source/NMS/GameComponents/GcTechnology.cs).
- [MBINCompiler inventory element schema](https://github.com/monkeyman192/MBINCompiler/blob/development/libMBIN/Source/NMS/GameComponents/GcInventoryElement.cs). The development branch can change; it is not the executable guard.

## Smallest next proof

1. Statically follow the current native technology-recharge action from the
   existing quick-menu dispatcher, identifying the inventory choice, element
   validation, charge update and resource debit separately. The historical
   `Charge`/`ChargeMenu` enum names are search hints only. Verify return types,
   native thread/phase, caller-side work and failure behavior before proposing
   an adapter. Also trace one ordinary native technology drain; recharge and
   discharge may use different routines.
2. Build an offline injected-reader inventory snapshot helper, using synthetic
   stores. Require bounded counts, unique exact custom ID, fully installed and
   usable state, coherent charge bounds and context identity. Reject malformed,
   duplicated, absent or changing entries. Return copied values, never a durable
   native element pointer. It must not call native functions or write anything.
3. Only after those fields and the local update phase are verified, prepare a
   separate explicitly read-only game observer. Compare one known vanilla
   exosuit technology before/after the player recharges it normally. Cancel on
   load, application replacement, inventory relocation, packaging or context
   changes. Do not infer a stable pointer from one successful read.
4. Design the later charge transaction around a separately authenticated
   automatic summon outcome. Queue acceptance alone does not prove a pet became
   active. No debit on placement failure, no double debit on repeated callbacks,
   no periodic retries after dismissal, and no alteration of manual summoning.
   Multi-step battery consumption/refill additionally needs failure and rollback
   semantics from the game's own implementation.

The data prototype can proceed while these gates remain open. Actual inventory
mutation, charge persistence, normal install/recharge UI, save reload, packaged
technology transfer, uninstall behavior and multiplayer remain unverified.
This research does not establish safety for unmodified peers or a release-ready
mandatory technology requirement.
