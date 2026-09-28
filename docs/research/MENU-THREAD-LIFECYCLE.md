# Menu callback thread and lifecycle diagnostics

## Retained observation and source boundary

The immutable 090-r2 session logged `unexpected_thread` at 14:30:17 on
28 September 2026. Custom menu processing stopped; the native binding filter
remained installed, and later production summon diagnostics continued. The
message did not identify the failed callback, first thread or in-flight menu
transaction. See [LIVE-090](LIVE-090.md). No retained observation establishes
that teleporting or base removal caused the thread change or pet disappearance.

`tools/quick_menu_order_trial.py` pins `get_native_id()` on the first ordinary
callback accepted by `_enter`. That pin lasts for the entire Mod instance; a
later ordinary callback on another thread stops custom processing before its
native reads or writes. The callbacks can run while no CAS item is selected,
so the first callback is not necessarily the first visible CAS interaction.
Resource loading deliberately has a separate lock and neither reads nor pins
the ordinary callback thread. Build, activation and confirmation transactions
also have pairing/reentrancy checks. The previous generic stop record cleared
those transactions without retaining their diagnostic context.

This establishes the refusal mechanism, not whether a changed thread is safe.
No source evidence currently authorizes rebinding to another thread, accepting
concurrent callbacks or using teleport arrival as a lifecycle reset.

## Implemented source instrumentation

Menu **0.9.1-diagnostics**, prepared for a separate combined **0.9.2** candidate,
retains every thread/pairing refusal and the process-lifetime binding filter.
It adds only English developer diagnostics; player text, translations, input,
settings, production behavior and native mappings are unchanged. It has not
been deployed or tested in the game, and the active 090-r2 is untouched.

- Each of the eight fixed ordinary callback phases emits at most one first-seen
  record naming the phase and OS thread ID. Label callbacks now have the explicit
  name `label_after` rather than the unnamed `ordinary` phase.
- An owned 16-entry ring retains recent ordinary callback attempts: bounded
  sequence number, phase, OS thread ID and Boolean build/trigger/confirmation/
  confirmation-intent activity. Eight phase counters and the sequence saturate
  at 1,000,000. No per-frame log stream is created.
- The existing one-time stop warning now includes the attempted callback,
  observed thread, pinned thread, the phase that established the pin, and the
  pending lifecycle flags captured before cancellation. It also includes the
  bounded ring and counts. The additional flags describe whether the resource
  phase was seen, an item had been appended and the CAS submenu had opened.
- An append rejected by its earlier builder-thread check reports `append` before
  any incoming item read. Overlap records retain the original lock ownership;
  failed thread lookup is recorded as unavailable, without exception details.
- Trace bookkeeping uses a separate nonblocking lock. Contention skips an
  observation; a busy/unavailable snapshot says `unavailable`. These best-effort
  records are not synchronization proof and never authorize game operations.
  Logging failure does not disable ordinary work or weaken the safety guard.

Only fixed phase names, bounded counts, thread IDs and Boolean flags are logged.
There are no raw menu/item/action pointers, copied native fields, account/save
identities, pet names, file paths or extra native memory reads. No hook, RVA,
resource registration behavior, thread handoff or automatic retry was added.

## Offline verification

Focused verification passed **111 tests**: 36 ordered-menu adapter tests
(including ten new diagnostic regressions), 26 toggle tests, 29 settings/icon
tests and 20 language-observer tests. Locale validation still reports fourteen
catalogs with 46 keys and unchanged English native text.

The owned-memory/fake-hook tests verify:

- A label can establish the lifetime pin; a later builder on another thread is
  rejected before native reads, preserving the original pin and native filter.
- Mismatched builder completion, early append, pending activation and pending
  confirmation report the correct phase and pre-clear transaction state while
  preserving native results and preventing preference/native mutations.
- The ring, counters and first-seen logs remain bounded across repeated valid
  captions. A stopped menu emits no repeated diagnostic stream or native work.
- Logging failure, busy diagnostic bookkeeping, callback overlap and failed
  thread lookup retain safe cancellation and original lock ownership.
- Existing native ordering, control behavior and isolated resource-thread
  handling remain covered by the adapter regression suites.

These tests exercise synthetic owned buffers only. Their result does not show
which live callback changed thread or whether a safe lifecycle handoff exists.

## Next bounded live check

Use a separately validated candidate after normal closure and the required
backup. First verify ordinary menu opening and settings. If the guard stops,
retain the exact first-seen and failure records and the player's action sequence.
Compare the pin origin, failing phase and transaction flags; do not attribute
causality from a nearby teleport or base action alone. Additional targeted
native lifecycle research must precede any guard relaxation. Preserve OFF,
manual dismissal, native binding safety and the working production automation.
