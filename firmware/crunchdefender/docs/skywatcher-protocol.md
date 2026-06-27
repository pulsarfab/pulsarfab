# Skywatcher Motor-Controller Serial Protocol

This document describes the serial command set used by Skywatcher mounts
(EQ6-R, AZ-EQ5/6, EQ8, HEQ5, AZ-GTi, Wave-150i / strain-wave models,
Star Adventurer, etc.) as observed in the [GSServer][gss] source. It is
the reference for the inline parser running on the CrunchDefender, which
sits between the PC (USB host) and the Skywatcher hand controller / WiFi
adapter / direct-motor-controller USB port (USB device side of the link).

The protocol originates from the SynScan "motor controller" command set,
documented informally by Andrew Johansen and the `skywatcher-pacific`
project. There is no official ST datasheet — these notes are derived
from `GS.SkyWatcher/Commands.cs` in [rmorgan001/GSServer][gss] (GPL-v3).

[gss]: https://github.com/rmorgan001/GSServer/

## Wire format

- **Transport**: UART, 9600 8N1, no flow control (the USB endpoint on
  modern controllers is a CDC-ACM adapter — the protocol on the wire is
  identical to the legacy RS-232 ports).
- **Framing**: each frame is terminated by a single `CR` (0x0D = `\r`).
  There is *no* LF.
- **Encoding**: all numeric payloads are **uppercase ASCII hex**
  (`0-9A-F`). Lowercase hex is rejected with error `!3`.
- **Direction is explicit per frame**. The host sends frames starting
  with `:`, the mount replies with frames starting with `=` (success) or
  `!` (error).

### Host → Mount

```
':' <cmd> <axis> [data...] CR
```

| Byte | Meaning |
|------|---------|
| `:`  | Start-of-command marker (literal colon) |
| `<cmd>` | 1 ASCII letter, case-sensitive — selects the command |
| `<axis>` | `1` = RA / azimuth, `2` = Dec / altitude |
| `<data>` | 0–18 ASCII hex chars (command-dependent) |
| `CR`  | 0x0D terminator |

GSServer caps the outbound buffer at 20 bytes (`bufferSize = 20`) which
covers every command in the set.

### Mount → Host

```
'=' [data...] CR              (success)
'!' <code> CR                  (error)
```

| Reply | Meaning |
|-------|---------|
| `=CR` | Bare success, no payload (used by setters like `S`, `H`, `K`, `J`, `G`, `M`, `U`, `V`, `W`, `O`, `P`, `E`, `F`, `L`) |
| `=DDDDDDCR` | 24-bit unsigned value, **byte-reversed hex** (see below) |
| `=DDDDDDDDCR` | 32-bit value (advanced command set only) |
| `=DDD…CR` | Wider response (`X000F` returns 33 chars; `X0005` etc.) |
| `!CR` | Generic error, no code |
| `!nCR` | Error code (see [Error codes](#error-codes)) |

#### "Byte-reversed hex" — the 24-bit response encoding

This is the single weirdest part of the protocol. The original
6-character responses are not big-endian or little-endian hex of a
24-bit number — they are little-endian **byte-pair** hex. GSServer's
`StringToLong` reconstructs the integer as:

```c
value = parse_hex(s[0:2]) * 16^0
      + parse_hex(s[2:4]) * 16^2
      + parse_hex(s[4:6]) * 16^4
```

So response `"563412"` decodes to `0x123456`. The matching `LongToHex`
emits the low byte first. Plain English: think of it as little-endian
storage with each byte already printed as two hex characters.

The advanced command set (`:X…`, firmware ≥ 3.22) uses straightforward
big-endian 32-bit hex (`String32ToInt` does a plain `int.Parse(…,
NumberStyles.HexNumber)`).

#### Position offset

In the legacy command set, axis positions are biased by `0x800000` so
that 24-bit unsigned values can represent both directions around home:

- raw `0x800000` ⇒ position `0`
- raw `0x800001` ⇒ position `+1` step
- raw `0x7FFFFF` ⇒ position `-1` step

GSServer always subtracts `0x800000` before using the value. The
advanced command set uses signed 32-bit two's complement — no offset.

### Detection / capability negotiation

1. Send `:e1` (or `:e2`) to read the axis firmware version. The
   response is 6 hex chars decoding (via `StringToLong`) to a 24-bit
   value laid out as `MM mm ID` — model in the high byte, minor in the
   middle, *no, wait*: GSServer parses it as
   `first = response[1:3]`, `second = response[3:5]`,
   `mountModel = response[5:7]`. After the byte-reversal, `first.second`
   is the firmware version (e.g. `3.27`) and `mountModel` is one of:

   | Model byte | Mount |
   |------------|-------|
   | `0x00`     | EQ6 |
   | `0x01`     | HEQ5 |
   | `0x02`     | EQ5 |
   | `0x03`     | EQ3 |
   | `0x04`     | EQ8 |
   | `0x05`     | AZ-EQ6 |
   | `0x06`     | AZ-EQ5 |
   | `0x07`–`0x0A`, `0x0F` | Single-axis trackers (Star Adventurer family) |
   | `0x80`     | 80GT — forced step count `0x162B97` |
   | `0x82`     | 114GT — forced step count `0x205318` |
   | `0xA5` (165) | AZ-GTi |

2. If the firmware version is **> 3.22** the controller supports the
   *advanced command set* — the `:X…` family with 32-bit signed values
   and a different set of subcommands. GSServer exposes this as the
   `SupportAdvancedCommandSet` flag and prefers `:X…` when available
   and `AllowAdvancedCommandSet` is enabled.
3. The AZ-GTi (model `0xA5`) needs firmware ≥ 3.40 for advanced support;
   the Star Adventurer (`0x038207` = 3.130.07) is excluded entirely.

## Command reference

The table below lists every single-letter command observed in
GSServer's `Commands.cs`, with its arguments, response, and the
GSServer call sites that emit it. Axis number is appended to every
command (`:e1`, `:e2`).

| Cmd | Direction | Data | Response | Purpose |
|-----|-----------|------|----------|---------|
| `a` | get | — | `=hhhhhh` | Steps per revolution. Override `0x162B97` for 80GT, `0x205318` for 114GT |
| `b` | get | — | `=hhhhhh` | Timer interrupt frequency (used to convert rates → step periods) |
| `c` | get | — | `=hhhhhh` | Micro-steps from target where ramp-down begins |
| `d` | get | — | `=hhhhhh` | **Current encoder count** (the "true" axis position, independent of `j`) |
| `D` | get | — | `=hhhhhh` | Sidereal rate in step counts |
| `e` | get | — | `=hhhhhh` | Firmware version + mount model (see [detection](#detection--capability-negotiation)) |
| `E` | set | `hhhhhh` | `=` | Set axis position counter. Value is biased by `+0x800000` |
| `f` | get | — | `=ABC` (3 hex) | Axis status (see below) |
| `F` | set | — | `=` | Initialize / energize axis motor controller |
| `g` | get | — | `=hhhhhh` | High-speed multiplier (16 for EQ6Pro / AZ-EQ5 / EQ8, 32 for AZ-EQ6) |
| `G` | set | `fd` (2 ASCII) | `=` | Set motion mode. `f` ∈ `0..3`: `0` hi-speed GOTO, `1` lo-speed slew, `2` lo-speed GOTO, `3` hi-speed slew. `d` ∈ `0/1`, swapped in the southern hemisphere |
| `h` | get | — | `=hhhhhh` | Current GOTO target |
| `H` | set | `hhhhhh` | `=` | Set GOTO target increment (steps from current position) |
| `i` | get | — | `=hhhhhh` | Last slew speed (timer ticks / 1024 s) |
| `I` | set | `hhhhhh` | `=` | Set slewing rate — value is the number of timer ticks between motor steps. Higher = slower |
| `j` | get | — | `=hhhhhh` | Axis position (biased by `0x800000`). The most common command in normal operation |
| `J` | set | — | `=` | Start motion using the previously configured mode/rate/target |
| `K` | set | — | `=` | Stop axis (graceful, ramp-down) |
| `L` | set | — | `=` | Stop axis (instant — no ramp) |
| `M` | set | `hhhhhh` | `=` | Set break-point increment (where ramp-down starts in steps before target) |
| `O` | set | `0`/`1` | `=` | Snap-port (DSLR shutter trigger) off/on |
| `P` | set | `0..4` | `=` | ST4 guide rate: `0`=×1.00, `1`=×0.75, `2`=×0.50, `3`=×0.25, `4`=×0.125 of sidereal |
| `q` | get/set | `0Xnnnn` | `=hhhhhh` | Capabilities / extended status (see `q` subcommands below) |
| `s` | get | — | `=hhhhhh` | PEC period in steps (worm CPR) |
| `S` | set | `hhhhhh` | `=` | Set absolute GOTO target position |
| `U` | set | `hhhhhh` | `=` | Set brake-step count |
| `V` | set | `hh` | `=` | Polar-scope LED brightness, `0x00..0xFF` |
| `W` | set | `nXnnnn` | `=` | Misc toggles (see `W` subcommands below) |
| `X` | get/set | varies | varies | Advanced command set (firmware ≥ 3.22, see `X` subcommands below) |

### `:f` axis status word

`:f` returns a 3-character hex response `ABC` interpreted bit-wise:

```
char[1] (B):  bit 0 = 1 → slewing (continuous), 0 → goto-to-target
              bit 1 = 0 → forward direction
              bit 2 = 1 → high-speed mode

char[2] (C):  bit 0 = 0 → at full stop (motor halted)
                      1 → axis is running

char[3] (D, sometimes called response[3]):
              bit 0 = 1 → axis initialized (`F` has been issued)
              bit 2 = 1 → low-voltage event latched
```

Refer to `Commands.cs:GetAxisStatus`.

### `:q` subcommands (legacy capabilities & sensor read-out)

Encoded as `:q<axis>nnnnnn` where the 6 hex chars are interpreted as a
24-bit value via `LongToHex(n)`.

| Subcmd argument | Meaning |
|-----------------|---------|
| `0`  → `000000` | Home-sensor latched position. Special returns: `=000000` (CW of home, sensor reset), `=FFFFFF` (CCW of home, sensor reset), any other value = position at which the home sensor last tripped. Send `:Wx08` to re-arm. |
| `1`  → `010000` | Capability nibbles `ABCDEF` (see below) |
| `3`  → `030000` | Controller bus voltage. Decoded value / 100.0 = volts (e.g. `=0E0500` → 5.39 V) |

#### `:qx010000` capabilities response

The response is `=ABCDEF` where each nibble is a bitfield:

| Nibble | Bit 8 | Bit 4 | Bit 2 | Bit 1 |
|--------|-------|-------|-------|-------|
| **A**  | —     | —     | pPEC ON now | pPEC training in progress |
| **B**  | Supports AZ/EQ modes | Has home sensors | Supports pPEC | Supports dual encoders |
| **C**  | Has WiFi | Supports half-current tracking (`:Wx06…`) | Axes must start independently (can't use `:J3`) | Has polar LED |

### `:W` subcommands

Encoded as `:W<axis>nXnnnn` where the first hex digit selects the
function (1-byte command in the high nibble pair).

| Encoded data | Meaning |
|---|---|
| `000000` | pPEC training **on** |
| `010000` | pPEC training **off** |
| `020000` | pPEC playback **on** |
| `030000` | pPEC playback **off** |
| `040000` | Encoders **on** (dual-encoder mounts) |
| `050000` | Encoders **off** |
| `060000` | Low-speed full-current **off** (half-current tracking enabled) |
| `060100` | Low-speed full-current **on** |
| `070000` | Set stride for slewing |
| `080000` | Reset / re-arm home-position index sensor |

### `:X` subcommands (advanced command set)

`:X` payloads start with a 2-hex-digit *function code*, followed by
function-specific data. Values are **straight big-endian hex** —
no byte reversal. The full subcommand catalogue observed in GSServer:

| Function | Form | Direction | Meaning |
|----------|------|-----------|---------|
| `0001` | `:X<axis>0001` | get | Axis status word (32-bit). Bit 0 = slewing, bit 2 = trajectory mode, bit 6 = initialized, bit 10 = low-voltage latch |
| `0002` | `:X<axis>0002` | get | Counts per revolution (32-bit, used with resolution factor for 256-µstep drivers) |
| `0003` | `:X<axis>0003` | get | Axis position (32-bit signed, two's complement, **no `0x800000` bias**) |
| `0005` | `:X<axis>0005` | get | MountID + firmware version, advanced form |
| `0007` | `:X<axis>0007` | get | Current slew speed (ticks / 1024 s) |
| `000B` | `:X<axis>000B` | get | 32-bit home-sensor latched position |
| `000E` | `:X<axis>000E` | get | Worm resolution (CPR) for PEC |
| `000F<8hex>` | `:X<axis>000F<8hex>` | get | Atomic positions+timestamp snapshot. Response is 33 chars: `=<RA:8><Dec:8><microseconds:16>`. The argument is a context/sequence pad |
| `01<8hex>` | `:X<axis>01<8hex>` | set | Set axis position counter to signed value |
| `02<16hex>` | `:X<axis>02<16hex>` | set | Slew at signed rate (steps/1024 s, padded with `F` for negative two's complement) |
| `04<8hex><16hex>` | `:X<axis>04<target><rate>` | set | Slew to absolute position, then hold at zero velocity |
| `0500` | `:X<axis>0500` | set | Snap-port on |
| `0501` | `:X<axis>0501` | set | Snap-port off |
| `0504` | `:X<axis>0504` | set | Stop axis (graceful) — advanced replacement for `:K` |
| `0505` | `:X<axis>0505` | set | Initialize axis — advanced replacement for `:F` |

GSServer pads negative two's-complement hex with `F` on the left
(`PadLeft(16, 'F')`), so `-1` becomes `FFFFFFFFFFFFFFFF`. The
CrunchDefender parser must reproduce this when emitting commands.

## Error codes

The reply `!c` (single trailing char `c`) indicates one of:

| Code | Meaning | Notes |
|------|---------|-------|
| (none)  | Invalid reason code | GSServer falls back to `=000000` if cmd was `q` |
| `!0` | **Unknown command** — not implemented on this model | GSServer also synthesises `=000000` for `q`/`W` to keep state machines moving |
| `!1` | Invalid param count | wrong-length data |
| `!2` | Motor not stopped — can't run this command while moving | GSServer responds by sending `:K` on the same axis and sleeping 500 ms |
| `!3` | Non-hex parameter — contains a lowercase or non-hex char |
| `!4` | Motor not energized — issue `:F` first |
| `!5` | Driver asleep — controller in sleep mode |
| `!6` | Mount is not tracking |
| `!7` | Unknown (reserved) |
| `!8` | Invalid pPEC model |
| `!9` | Invalid command (different from `!0` — malformed parsing) |
| `!A` | Extra following data overtime — trailing bytes after terminator |

## Sequencing notes

Things the CrunchDefender parser must respect:

1. **Locking** — only one outstanding command per axis. GSServer
   serialises with a `Monitor.TryEnter` lock and a 50 ms timeout,
   retrying up to 6 times. The mount itself silently drops overlapping
   commands.
2. **Discard before send** — GSServer flushes both serial buffers
   before every `SendRequest`. The mount sometimes leaves stale junk
   on the line after a reset.
3. **Up to 10 retries on empty response** before bailing — if a
   response is `null`, GSServer retries with a 10 ms sleep between
   attempts and increments a continuous-error counter. After
   `ConErrMax = 50` consecutive misses it gives up with
   `ErrTooManyRetries`.
4. **Timeout panic stop** — on read timeout, GSServer immediately
   sends `:K1` *and* `:K2` (stop both axes) and raises
   `ErrNoResponseAxis…`. The CrunchDefender should mirror this: if
   the host link goes silent mid-move, both axes must be commanded to
   stop, since the mount will otherwise continue at its last
   commanded rate indefinitely.
5. **`:j` may legitimately return nothing** — the mount sometimes
   drops a position response under load, so callers pass
   `ignoreWarnings = true`. The parser must not treat a missing `:j`
   reply as an error condition.
6. **Goto target setup is multi-step** — a typical "slew to position"
   sequence is `:G` (mode) → `:I` (speed) → `:H` (target increment) →
   `:M` (brake point) → `:J` (start). The advanced equivalent is the
   single `:X04…` command.

## Typical command exchange — example slew

Below is a goto-then-track on Axis 1 (legacy command set), with bytes
shown in time order:

```
host → mount   :K1\r                        ; ensure stopped
mount → host   =\r
host → mount   :G120\r                      ; mode=lo-speed-GOTO, dir=forward
mount → host   =\r
host → mount   :I100100\r                   ; slewing rate (timer ticks)
mount → host   =\r
host → mount   :H001000\r                   ; target = +0x1000 steps from here
mount → host   =\r
host → mount   :M000200\r                   ; brake when 0x200 steps from target
mount → host   =\r
host → mount   :J1\r                        ; go
mount → host   =\r
host → mount   :j1\r                        ; (subsequently, position polling)
mount → host   =01F003\r                    ; little-endian-byte-pair => 0x03F001
                                            ; then subtract 0x800000 => -8,420,863 steps
```

## What the CrunchDefender cares about

For limit enforcement, the parser only **needs** to track:

1. **Position** — observe every `:j`, `:d`, `:X0003`, `:X000F` reply
   to maintain a current axis position estimate.
2. **Motion intent** — observe every `:H`, `:S`, `:G`, `:I`, `:J`,
   `:X02…`, `:X04…` *command* to know which way and how fast the host
   is asking the mount to move next.
3. **Stops** — observe every `:K`, `:L`, `:X0504` so the parser knows
   the mount is being commanded to a halt and clears any pending
   limit warning.
4. **Axis re-zero** — observe `:E` and `:X01…` to know when the host
   has redefined the position origin (limits must be re-evaluated in
   the new frame).

Everything else (pPEC, snap-port, polar LED, ST4 rate, sensor reads)
can be passed through transparently.

The parser does **not** need to fully decode every command — only
recognise the leading `:`, command char, axis digit, and length to
know when a frame ends and whether to capture its payload. The wire
format is simple enough that a 16-state byte-level state machine on
the F405 (one per direction) is sufficient at 9600 baud.

## Autohome

There is **no mount-side "autohome" command**. Autohome on the
Skywatcher controllers that support it (those with the home-sensor
capability bit set — EQ8, AZ-EQ6, AZ-EQ5, AZ-GTi, Wave-150i, EQ6-R
Pro) is implemented as a host-side state machine that combines three
existing protocol primitives:

| Protocol primitive | Used for |
|---|---|
| `:qx010000` (legacy) — nibble **B bit 4** | Capability check: does this mount have a home sensor at all? |
| `:Wx080000` | Reset / re-arm the home-sensor latch |
| `:qx000000` (legacy) or `:X<n>000B` (advanced) | Read the latched home-trip position |
| Normal motion commands (`:G`, `:I`, `:H`, `:M`, `:J`, or `:X02…` / `:X04…`) | Move the axis to scan for the sensor |

### How GSServer's `AutoHomeSky.cs` orchestrates these

The algorithm is per-axis and runs entirely in the host. Refer to
`GS.Server/AutoHome/AutohomeSky.cs:StartAutoHome`.

1. Check `SkyCanHomeSensors` (reads `:qx01`). Abort with
   `HomeCapabilityCheckFailed` if the sensor capability bit is not set.
2. Stop tracking; stop the axis (`:K` / `:X0504`).
3. Capture the configured "park / home" position as a reference
   baseline.
4. Slew 3.3° away from the current position — in case the axis was
   already sitting on top of the home sensor.
5. **Bracket loop**, repeated up to `maxMove / 5` times (default
   `maxMove = 100°`):
   - Reset the latch (`:Wx08…`), then poll `:qx00…` (or `:X000B`) to
     determine which side of the home flag the axis is currently on:
     - `=000000` / `=80000000` → "armed, CW side of home"
     - `=FFFFFF` / `=7FFFFFFF` → "armed, CCW side of home"
     - anything else → **trip — the latched value is the axis position
       at which the sensor fired**
   - If the latch is still armed, slew 5° in the direction implied by
     the side-of-home flag (toward home), and check again.
   - If the side-of-home flag changed without a trip being captured,
     refine with a 2.5° slew and re-check; restart the search up to
     two times (`startOvers ≥ 2` → `TooManyRestarts`).
6. Once `:qx00…` returns a trip value, slew the axis to that step
   position (`SlewToHome` → server-side goto).
7. **Validation pass:**
   - Slew 3.7° away from the detected home.
   - Reset latch and re-poll — confirm armed.
   - Slew 5° back across home — confirm the latch trips again.
8. **Backlash removal:** slew 3° in the opposite direction.
9. Final slew to the latched home position.
10. Optional Dec offset (for side-saddle mounts where the OTA balance
    point isn't on the mechanical home).

If the user requests an abort mid-run (`AutoHomeStop`), GSServer bails
out at the next check and returns `StopRequested`. Any motion timeout
or empty serial response triggers the standard panic-stop on both
axes via `:K1` / `:K2`.

### Implication for the CrunchDefender parser

This is the key insight for the limit guard:

> Autohome traffic is **indistinguishable** from normal slew traffic on
> the wire. The same `:G/:I/:H/:M/:J` (or `:X04…`) commands move the
> axis. The only signature is the periodic `:Wx08…` reset and the
> `:qx00…` / `:X000B` polls before each scan step.

The parser should:

1. **Detect autohome mode** by watching for repeated `:Wx<axis>080000`
   commands. A single `:W…08…` could be a manual sensor reset; three
   or more within ~10 seconds is almost certainly an autohome run.
2. **While autohome is suspected**, either:
   - relax the configured soft limits (since autohome legitimately
     sweeps several degrees in unpredictable directions until the
     sensor trips), **or**
   - leave hard limits in place and trust the host to stop on the
     first sensor trip — but be ready to fire a `:K` / `:L` if the
     scan exceeds the host's own `maxMove` (default 100° per axis,
     enough to slam through a soft limit on most setups).
3. **Exit autohome mode** when the host stops issuing `:Wx08…` resets
   for ≥ 30 seconds, or sends a normal `:S` / `:H` GOTO outside the
   autohome scan pattern.
4. **Re-zero awareness** — autohome ends by issuing `:E` / `:X01…` to
   set the axis position counter to the calibrated home value. The
   parser must observe this and recompute its limit bookkeeping in
   the new frame (same as for a manual sync).

### Mounts without home sensors

Synta / Skywatcher mounts that do **not** have home sensors (HEQ5,
EQ6 non-R, EQ5, EQ3, basic AZ-GTi pre-3.40) report capability nibble
B bit 4 = 0 and reject `:Wx08…` and `:qx00…` with `!0` (unknown
command). On those mounts:

- The host has no way to find a mechanical home — it relies entirely
  on the user setting the OTA to a defined "park" position and
  zeroing via `:E` / `:X01…`.
- The CrunchDefender's limit bookkeeping is anchored to whatever
  position the user manually told the host was home; any drift due to
  unintentional movement (cable snag, etc.) will silently shift the
  limit envelope. This is a fundamental limitation of the protocol
  and not something the limit guard can correct for — only flag.
