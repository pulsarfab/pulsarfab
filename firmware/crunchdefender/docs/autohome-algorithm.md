# Skywatcher Autohome Algorithm — Detailed Walkthrough

This is a deep dive into the autohome state machine as implemented in
[`GS.Server/AutoHome/AutohomeSky.cs`][autohome] (GSServer, GPL-v3). The
[Autohome section of the protocol doc](skywatcher-protocol.md#autohome)
has a condensed version; this file is the detailed reference.

[autohome]: https://github.com/rmorgan001/GSServer/blob/master/GS.Server/AutoHome/AutohomeSky.cs

The autohome function is **not a mount command**. It is a host-side
algorithm that combines three protocol primitives:

| Primitive | Purpose |
|---|---|
| `:qx010000` nibble B bit 4 | Capability check |
| `:Wx<axis>080000` | Reset / re-arm the home-sensor latch |
| `:qx<axis>000000` (legacy) or `:X<axis>000B` (advanced) | Read the latched home-trip position |

The mount provides a one-shot optical or Hall-effect flag latch per
axis. The host has to *find* the flag by scanning, recognise when the
latch trips, and refine to the trip position. There is no continuous
"distance to home" feedback signal.

## The primitive: `GetHomeSensorStatus(axis)`

This is the only piece of mount data the algorithm consumes. It maps
five possible mount responses to a tri-state result:

| Wire response | Internal long (after `GetHomePosition` mapping) | `GetHomeSensorStatus` returns | Meaning |
|---|---|---|---|
| `=80000000` (advanced) | `100000000000` | `true` | Sensor **armed**, axis is on the CW (negative) side of the flag |
| `=000000` (legacy) | `300000000000` | `true` | same — armed, CW side |
| `=7FFFFFFF` (advanced) | `200000000000` | `false` | Sensor **armed**, axis is on the CCW (positive) side |
| `=FFFFFF` (legacy) | `400000000000` | `false` | same — armed, CCW side |
| any other value | `< 100000000000` | `null` ⚠️ **side effect**: writes value into `TripPosition` field | Sensor **tripped** — the value is the axis step position at the moment it fired |

The four "armed" sentinels are 32-bit min / max and 24-bit zero / max
— the mount uses them as flags rather than as real positions. **The
tristate `true` / `false` / `null` is the entire vocabulary the
algorithm has to work with.** `null` is the success signal.

`GetValidStatus` wraps this with a `:Wx080000` reset + up to 2 retries:
if the first read returns `null` (already-stored trip), it resets,
slews 1°, and tries again. This guards against stale latch data left
over from a previous run.

## Control flow

```
                            ┌─────────────────────────────┐
   ┌──── start ────────────►│ Capability check (:qx01 B.4) │── no ──► HomeCapabilityCheckFailed
   │                        └─────────────────────────────┘
   │                                       │ yes
   │                                       ▼
   │                        ┌─────────────────────────────┐
   │                        │ Stop axis, kill tracking,    │
   │                        │ snapshot configured home pos │
   │                        └─────────────────────────────┘
   │                                       │
   │                                       ▼
   │                  Phase A: slew +3.3°  (unconditional, default direction)
   │                                       │
   │                                       ▼
   │  ┌────────────────────────────────────────────────────────────────────┐
   │  │ Phase B: bracket loop — up to (maxMove/5) iterations               │
   │  │                                                                    │
   │  │   status = GetValidStatus()        ← :Wx08 reset + :qx00/:X000B   │
   │  │   if status==null   → goto Phase C  (trip already captured)        │
   │  │                                                                    │
   │  │   if previous loop also armed AND direction flipped:               │
   │  │       slew 2.7° in current scan direction                          │
   │  │       re-read sensor                                               │
   │  │       if still armed → startOvers++, restart loop                  │
   │  │       else            → goto Phase C  (bracket succeeded)          │
   │  │                                                                    │
   │  │   clockwise = (status == true)     ← scan toward home              │
   │  │   slew 5° in clockwise direction                                   │
   │  │   totalMove += 5°                                                  │
   │  │                                                                    │
   │  │   status' = GetHomeSensorStatus()   ← NO reset this time          │
   │  │   if status' == null               → goto Phase C                  │
   │  │   if status' != lastStatus:                                        │
   │  │       slew 2.5° in same direction                                  │
   │  │       re-read                                                      │
   │  │       still armed? startOvers++, restart                           │
   │  │       else            → goto Phase C                               │
   │  │                                                                    │
   │  │   abort guards:  totalMove ≥ maxMove → HomeSensorNotFound          │
   │  │                  startOvers ≥ 2      → TooManyRestarts             │
   │  │                  AutoHomeStop         → StopRequested              │
   │  └────────────────────────────────────────────────────────────────────┘
   │                                       │
   │                                       ▼
   │       Phase C: Slew axis to TripPosition (via server-side goto)
   │                                       │
   │                                       ▼
   │       Phase D: Validation
   │            slew 3.7° AWAY from home (default direction)
   │            GetValidStatus() → expect armed (not null)
   │            clockwise = (status == true)
   │            slew 5° back across home
   │            GetHomeSensorStatus() → expect null (tripped)
   │            if not null → HomeSensorNotFound
   │                                       │
   │                                       ▼
   │       Phase E: Backlash removal
   │            slew 3° in the OPPOSITE direction (!clockwise)
   │                                       │
   │                                       ▼
   │       Phase F: Final slew to TripPosition
   │                                       │
   │                                       ▼
   │       Phase G (optional): if axis==Axis2 and |offSetDec|>0
   │            slew |offSetDec| with sign = (offSetDec<0)
   │                                       │
   │                                       ▼
   └────────────────────────── return Success
```

## Why each phase looks the way it does

### Phase A — the unconditional 3.3° kick

If the axis happens to be parked sitting on the home flag at startup,
`:qx00` will keep returning a stale trip value or oscillate between
"armed" and "tripped" as the latch is reset. The 3.3° pre-offset gets
you off the flag before the scan starts.

### Phase B — bracketing rather than direct seek

The home sensor is a **one-shot latch**: it stores the axis position
at which the optical/Hall flag was first crossed *after the last
reset*. The algorithm has no continuous "you are here relative to the
flag" signal — only "armed, you're on side X" or "tripped at position
P". So it has to:

1. Pick a scan direction (decided by which side `:qx00` says you're on).
2. Move a chunk in that direction.
3. Re-read.
   - If still armed and the side is unchanged: keep going.
   - If side flipped without a trip captured: you overshot the flag
     faster than polling could catch — refine with a smaller scan in
     the same direction. The latch should have been set during the
     crossing.
4. Best case: while moving, the latch trips and the next read returns
   `null` with the trip step count captured.

There are two refinement branches with slightly different magnitudes:

- **Top-of-loop flip** (the *previous* loop's status differed from
  this loop's): refine with a **2.7°** slew.
- **Within-loop flip** (status after the 5° slew differs from the
  status before): refine with a **2.5°** slew.

The two values are likely empirical — there's no obvious geometric
reason for the difference. They're both close to the typical home-flag
width on the EQ8/AZ-EQ6 mechanical setup.

### The "side flipped without trip" anomaly

This means the axis crossed the flag faster than the polling could
catch — physically possible at fast slew rates if the flag is narrow.
The latch *should* have been set during the crossing. If after the
re-scan the read **still** returns armed, the latch behaviour is wrong
(sensor stuck, controller bug, mechanical issue) — `startOvers++`,
loop again. After two such restarts the algorithm gives up with
`TooManyRestarts`.

### Restart caps

| Cap | Triggers | Meaning |
|---|---|---|
| `totalMove ≥ maxMove` (default 100°) | `HomeSensorNotFound` | Hard travel limit so the scope can't unwind cables searching for a sensor that's missing or jammed |
| `startOvers ≥ 2` | `TooManyRestarts` | Anomaly counter for the "flipped but no trip" case |
| `AutoHomeStop` flag set | `StopRequested` | User-initiated abort, checked at the top of every helper and between phases |

### Phase D — validation by re-tripping

A single sensor latch could be spurious (EMI, a single dust speck
across the optical interrupter, a tooth on a Hall flag aligning
borderline). Phase D deliberately backs off 3.7°, resets the latch,
and slews 5° back across the flag. If the latch trips again at roughly
the same position, you have a good detection. If not (status `!=
null` after the 5° back-slew → meaning "still armed, didn't trip"),
abort with `HomeSensorNotFound`.

**Note the subtle inversion of the success check here vs. Phase B —
in Phase B, `null` is the per-loop success signal; in Phase D, `null`
is the post-validation success signal but the test is structured the
other way around.** This is a code-clarity issue in GSServer, not a
behavioural difference.

### Phase E — backlash removal

Skywatcher worm-gear mounts have non-trivial backlash, on the order of
arcminutes to arcseconds depending on age and adjustment. The final
approach to home must come from a consistent direction so that the
home position is mechanically reproducible.

Phase E slews 3° in `!clockwise` (the opposite of the scan direction
that originally hit the flag). Phase F then slews back to
`TripPosition` from *that* side.

So home is always approached in the same direction the validation
pass approached it, which is the same direction the original detection
happened. This eliminates worm-gear lash from the final position.

### Phase G — the Dec offset

For mounts with the OTA mounted off the polar axis (side-saddle
configurations, dovetail rotated), mechanical "Dec sensor home"
doesn't correspond to "OTA pointing at the celestial pole / horizon".

Phase G lets the user nudge Axis 2 by a configured signed offset after
homing. It only runs on Axis 2, and the sign of the offset determines
direction (`offSetDec < 0` → reverse direction).

## Subtle bits that aren't obvious from a casual read

### The `clockwise` variable is a misnomer

It's the **scan direction**, and its sign flips with hemisphere in
`SlewAxis`:

```c#
case AxisId.Axis1:
    degrees = direction ? Math.Abs(degrees) : -Math.Abs(degrees);
    if (alignment != AltAz && southernHemisphere)
        degrees = direction ? -Math.Abs(degrees) : Math.Abs(degrees);
```

So "`clockwise == true` → `+degrees` → toward home" in the northern
hemisphere becomes "→ `−degrees`" in the southern hemisphere, and the
polarity of `:qx00`'s "CW side / CCW side" reporting has the opposite
physical meaning. The handling is implicit in `SlewAxis` rather than
factored out at the algorithm level — which makes the algorithm
hemisphere-agnostic to read, at the cost of confusing variable names.

### `TripPosition` is a class field, mutated as a side effect

`GetHomeSensorStatus` writes to `TripPosition` when it sees a trip
(non-sentinel response), and `SlewToHome` reads it back later in
Phase C / F without re-querying. The trip-position state is held
**off-mount, in the host process memory**.

This has two consequences:

1. If anything between the trip and `SlewToHome` resets the latch
   (e.g. an unrelated tool sending `:Wx08`), the field still holds the
   correct value — good.
2. If the host crashes mid-run, the trip position is lost — bad. A
   second autohome run starts from scratch; the mount's latched value
   would have been overwritten the next time the algorithm reset it.

For the **CrunchDefender parser**, this means: if you want to know
*where* home was, you must capture the `:qx00…` (or `:X000B`)
**response** that contained the trip value. By the time `SlewToHome`
fires, the trip value is no longer on the wire — it's in host memory.

### Phase B does `:Wx08` resets only inside `GetValidStatus`

The 5°-slew + re-read sequence inside the loop relies on the latch
from the previous reset still being valid. **Only `GetValidStatus`
issues `:Wx08…`**, and only at the top of each loop iteration (and
inside its own internal retry).

If the host or another tool sends an unsolicited `:Wx08` mid-scan, the
algorithm will see "armed" forever after the trip and either restart
or eventually fail with `HomeSensorNotFound`. **Concurrent autohome
requests from two clients will corrupt each other.**

For the CrunchDefender parser, this means `:Wx08…` traffic should be
treated as exclusive to whoever is driving — if you observe it
arriving from one source while a separate scan-style motion pattern is
already in progress from another, you have a multi-client conflict.

### `SlewAxis` blocks on `SkyServer.IsSlewing` polling at 300 ms

The motion is dispatched as a normal goto via `SkyServer.SlewAxes`,
which goes through the full server-side queue. There is **no rate
limiting between phases** — back-to-back Phase D / E / F slews can
fire in rapid succession, which is exactly the burst signature the
CrunchDefender should expect when autohome is running.

### `AutoHomeStop` checked at the top of every helper

A user-initiated abort never strands the mount mid-slew for more than
~300 ms (one IsSlewing-polling cycle). The check is in:

- `SlewAxis` (entry)
- `SlewToHome` (entry)
- `GetHomeSensorStatus` (indirectly via the loop checking before each
  call)
- Phase B loop top
- Between phases C/D/E/F

### Tracking is killed at start but not re-enabled at end

The post-condition is "axis is at home, tracking off". Re-enabling
sidereal tracking is the **host UI's** responsibility, not the
algorithm's. A successful return doesn't mean the mount is now
following the sky.

### The 0.7° offset between Phase A (3.3°) and Phase D (3.7°)

This is intentional. The validation slew starts at a slightly
different offset from the initial Phase A kick so that a
stuck-on-flag axis doesn't trivially "validate" by repeating the same
motion that found home. If the original detection was a spurious
trigger at a specific axis position, Phase D approaches from a
different starting position and is less likely to repeat the same
artefact.

### The diagnostic comparison at the end

```c#
var homeAxes = SkyServer.GetHomeAxes(...);  // snapshotted at start
...
var detectedPositions = Axes.MountAxis2Mount();
MonitorLog.LogToMonitor(...
    Message = $"AutoHome sensor vs initialised home|" +
              $"|HomeX:{homeAxes.X}|HomeY:{homeAxes.Y}" +
              $"|DetectedX:{detectedPositions[0]}|DetectedY:{detectedPositions[1]}" +
              $"|DeltaX:{detectedPositions[0] - homeAxes.X}|DeltaY:..."
);
```

This is purely **diagnostic telemetry** — it tells you how far the
configured "park position" was from the mechanical sensor. Useful drift
metric if you want to detect mount setup drift between sessions, but
the algorithm itself doesn't act on it.

## Failure modes summary

| Return value | Cause | What's left on the mount |
|---|---|---|
| `Success` | All phases passed | Axis at TripPosition, tracking off, latch reset |
| `HomeCapabilityCheckFailed` | `:qx01` nibble B bit 4 = 0 | No changes (no motion issued) |
| `HomeSensorNotFound` | Phase B exceeded `maxMove`, or Phase D didn't re-trip | Axis halted, position uncalibrated, tracking off |
| `TooManyRestarts` | Two "flipped but no trip" anomalies | Axis halted, position uncalibrated, tracking off |
| `FailedHomeSensorReset` | `GetValidStatus` couldn't get a valid armed-side reading | Axis halted, latch unknown state, tracking off |
| `StopRequested` | User aborted via `AutoHomeStop` flag | Axis halted wherever it was when checked, tracking off |

## What the CrunchDefender should do with this knowledge

1. **Detect autohome mode** by watching for repeated `:Wx<axis>080000`
   commands. A single `:W…08…` is ambiguous (could be a manual sensor
   reset by the user); **three or more within ~10 seconds** is almost
   certainly an autohome run.

2. **While autohome is suspected**, choose one of:
   - **Relaxed mode**: temporarily widen the configured soft limits.
     Autohome legitimately sweeps several degrees in unpredictable
     directions until the sensor trips, and ordinary slew limits will
     interrupt the scan.
   - **Backstop mode**: leave hard limits in place and trust the host
     to stop on the first sensor trip — but be ready to fire `:K` /
     `:L` if the scan exceeds the host's own `maxMove` (default 100°
     per axis, enough to slam through a soft limit on most setups).
   
   Backstop mode is the safer default for the CrunchDefender mission —
   the whole point of the device is to be a last line of defence
   against host bugs.

3. **Capture the trip position** from the `:qx00…` / `:X000B` response.
   The CrunchDefender can re-anchor its limit envelope to the
   mechanical sensor position rather than to whatever the host
   thinks "park" is. This is especially useful for mounts without
   absolute encoders (everything below the EQ8 in the Skywatcher
   lineup).

4. **Exit autohome mode** when one of:
   - The host stops issuing `:Wx08…` resets for ≥ 30 seconds.
   - The host sends a normal `:S` / `:H` GOTO outside the
     autohome scan pattern (large step delta, not the small
     2.5°/2.7°/3.0°/3.3°/3.7°/5° increments).
   - A `:E` / `:X01…` (set axis position counter) is observed —
     autohome ends by re-zeroing the axis to the calibrated home.
     **This is the canonical end-of-autohome signal.**

5. **Re-zero awareness** is critical. After observing `:E` / `:X01…`,
   the parser must recompute all limit envelopes in the new
   coordinate frame. Same handling applies to manual sync operations
   from a planetarium-software alignment routine.

## Reference values cheat-sheet

| Constant | Source | Value | Used for |
|---|---|---|---|
| Pre-offset | Phase A | 3.3° | Initial off-flag kick |
| Scan step | Phase B main | 5° | Each scan iteration |
| Top-of-loop refinement | Phase B | 2.7° | When previous-loop status flipped |
| Within-loop refinement | Phase B | 2.5° | When this-loop status flipped after 5° slew |
| Validation offset | Phase D | 3.7° | Slew-away before re-trip test |
| Validation re-trip | Phase D | 5° | Slew-back across home |
| Backlash removal | Phase E | 3° | Slew opposite direction |
| Max travel | parameter | 100° (default) | Hard search limit |
| Max restarts | hardcoded | 2 | Anomaly counter ceiling |
| Slewing poll | hardcoded | 300 ms | `IsSlewing` poll interval in `SlewAxis` |
| Internal retry slew | `GetValidStatus` | 1° | Per-retry probe within `GetValidStatus` |
