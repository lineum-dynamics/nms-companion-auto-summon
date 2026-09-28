# Native 0.10.0 r3 startup observation boundary

Recorded 28 September 2026 from read-only source/log inspection. The installed
runtime and frozen r3 package inputs were not changed. Personal logs, save
identities and companion identities are not copied into this record.

## Player observation and logged facts

The player first reported no visible companion after loading and a visible
companion after leaving the ship. They immediately qualified the first report:
they may simply have overlooked the startup companion. Therefore **startup
visibility is uncertain, not a confirmed failure**. Ship-exit visibility is
player-confirmed for this session.

The native UTC log records:

| Event | UTC time |
| --- | --- |
| Successful local save-load callback | 16:05:11.945 |
| First automatic opportunity armed | 16:05:30.074 |
| First native queue accepted | 16:05:32.660 |
| Second automatic opportunity armed | 16:05:55.204 |
| Second native queue accepted | 16:05:56.761 |

The first acceptance followed arming by 2.586 seconds; the second by 1.557
seconds. These are queue timings, not visible appearance timings. The log does
not attach an event-source, selected slot or location to the generic arming and
acceptance lines. Their association with load/exit follows the known callback
sequence and player report; the log alone does not independently label it.

Read-only preference inspection found automation and the three supported
locations enabled, with **By habitat** and **Shuffle companions** enabled.
Two consecutive accepted opportunities can select different companions. A
startup-versus-exit comparison must therefore control or record the selected
companion rather than assume that only startup timing changed.

## What the source currently establishes

`Runtime::afterLoad` records one deferred local opportunity; it performs no
placement or queue operation inside deserialization. `prepareLoad` waits for a
supported, enabled location and a positive finite ownership-update delta.
Normal policy then requires on-foot stability, ownership, placement and native
eligibility. A matching native queue acceptance consumes the policy request and
the selector reservation. Subsequent pet absence does not rearm anything.

This source contract explains why a working request appears in the log. It
cannot establish that the native game subsequently completed spawning or that
the player saw the pet. No faulty callback signature, lost load event or skipped
native request is demonstrated by the retained evidence.

The native port currently omits the maintained Python adapter's passive
post-queue lifecycle observer. After acceptance, native `tick` returns early
when neither a request nor a deferred load remains. The log therefore cannot
distinguish a queue still pending, logical activation, later deactivation or
an accepted queue that cleared before a logical active index was observed.

The owned-memory startup fixtures assert accepted queue calls, and their queue
service writes the pending slot. They do not simulate a renderer or infer
visible appearance. Their passing result must retain this scope.

The earlier Python [0.8.4 record](LIVE-084.md) already contains an accepted
startup request, a later matching logical active index and a report of no
visible pet, followed by a successful ship exit selecting another companion.
Later [0.8.7](LIVE-087.md) and [0.9.0](LIVE-090.md) include confirmed visible
startup pets. This history does not identify a cause or establish a new native
regression.

## Targeted next verification

Keep gameplay behavior unchanged. At a later normal restart, inspect the first
load independently before entering the ship or opening companion preview.
Record actual visibility and location. If comparing load and ship exit for a
specific pet, use the same known manually summonable companion deliberately;
do not silently change the player's saved mode or shuffle preference.

A later diagnostic-only candidate can port the existing passive observation
contract: at most 15 seconds, 4096 ownership callbacks and eight state-change
logs after acceptance, with the request source, slot, location, active/pending
indices and terminal reason. Observe before the no-op early return. Keep the
observer separate from policy, selector, placement, native eligibility and
queueing. Retain cancellation on settings/manual/context changes and bound
foreign callbacks. Read/log failures must stop only the observer.

Meaningful owned fixtures for that diagnostic candidate should cover:

- Accepted queue remaining pending, becoming active, or clearing without an
  observed active index, with no additional placement/queue calls.
- Activation followed by deliberate dismissal, with no automatic resurrection.
- Different companion, save, application, location, preview/emote or pending
  setting ending observation without changing summon policy.
- Observation deadlines, callback/log caps, invalid clocks, foreign ownership
  callbacks and read/log failures.
- Correct distinct event-source/slot records for load and ship exit.

Do not introduce a longer arbitrary spawn delay, retry after every absent pet,
or weaken native eligibility from this uncertain report. The notification
message-count and blocking-float fields are HUD-delivery conditions; they are
not established general world-readiness signals and must not be repurposed as
a startup gate without separate evidence.

No player-facing text or meaning changes arise from this record; locale files
remain unchanged.
