# PulsarFab Firmware

Firmware for PulsarFab dew heater controllers and mount accessories, written in
Rust. The STM32 targets use [Embassy](https://embassy.dev); the ESP32-S3 target
uses [`esp-idf-svc`](https://github.com/esp-rs/esp-idf-svc), which is Rust on
top of ESP-IDF.

## Projects

| Project | MCU | Flash | RAM | Package | Framework | Rust target | Status |
|---------|-----|-------|-----|---------|-----------|-------------|--------|
| **pulsardew** | STM32G0B1KBU6 | 128KB | 144KB | UFQFPN-32 | embassy-stm32 | `thumbv6m-none-eabi` | 🚧 Development |
| **pulsardewpro** | ESP32-S3-MINI-1 | 8MB | 512KB | Module | esp-idf-svc (std) | `xtensa-esp32s3-espidf` | 🚧 Development |
| **crunchdefender** | STM32F405RGT6 | 1024KB | 192KB | LQFP-64 | embassy-stm32 | `thumbv7em-none-eabihf` | 🌱 Bootstrapped |

Each project is its own cargo package rather than one workspace, because each
builds for a different target and pins a different toolchain.

## Project Structure

```
firmware/
├── Makefile                    # Build, flash and check targets
├── rust-toolchain.toml         # Stable, plus the two ARM targets
├── shared/                     # pulsarfab-shared: no_std code common to all
│   └── src/dewpoint.rs         # Dew point maths, unit-tested on the host
├── pulsardew/                  # STM32G0B1 USB dew heater
│   ├── .cargo/config.toml      # Target, probe-rs runner, link args
│   ├── src/clock.rs            # 16 MHz HSI -> 64 MHz SYSCLK
│   └── src/main.rs
├── crunchdefender/             # STM32F405 dual-USB mount limit guard
│   ├── .cargo/config.toml
│   ├── src/clock.rs            # 8 MHz HSE -> 168 MHz SYSCLK, 48 MHz USB
│   ├── src/main.rs
│   └── docs/                   # Skywatcher protocol notes
└── pulsardewpro/               # ESP32-S3 WiFi dew heater (ASCOM Alpaca)
    ├── .cargo/config.toml
    ├── rust-toolchain.toml     # Overrides the parent: Xtensa needs the fork
    ├── sdkconfig.defaults      # ESP-IDF configuration
    └── src/main.rs
```

The linker scripts, startup assembly and vendored ST HAL are gone.
`embassy-stm32` generates the memory map from its `memory-x` feature, and
`cortex-m-rt` provides the vector table and reset handler.

## Prerequisites

### For the STM32 targets

1. **Rust**, via [rustup](https://rustup.rs). `rust-toolchain.toml` pulls in the
   right toolchain and both ARM targets on first build.

2. **probe-rs**, to flash and to read `defmt` logs:

   ```bash
   cargo install probe-rs-tools
   ```

3. **ARM binutils**, for `arm-none-eabi-size` and `-objcopy`:
   - Fedora: `sudo dnf install arm-none-eabi-binutils-cs`
   - Ubuntu/Debian: `sudo apt install binutils-arm-none-eabi`
   - macOS: `brew install --cask gcc-arm-embedded`

4. **st-flash** (optional), if you would rather flash with an ST-Link than with
   probe-rs.

### For the ESP32-S3 target

The ESP32-S3 is an Xtensa part, and Xtensa is not an upstream Rust target. You
need Espressif's Rust fork:

```bash
cargo install espup
espup install
source ~/export-esp.sh      # add this to your shell profile
cargo install ldproxy espflash
```

The first `cargo build` then clones and builds ESP-IDF v5.4 under
`pulsardewpro/.embuild/`, which takes a while. Later builds reuse it.

If the build stops with `This script was called from a virtual environment,
can not create a virtual environment again`, some other tool has put a Python
virtualenv on your `PATH` — PlatformIO's `~/.platformio/penv/bin` is the usual
culprit. ESP-IDF builds its own virtualenv and will not nest one inside
another. Drop the offending directory from `PATH` and build again.

## Building

```bash
make pulsardew-g0b1            # Build pulsardew
make crunchdefender-f405       # Build crunchdefender
make pulsardewpro              # Build pulsardewpro
make help                      # Everything else
```

Or run cargo directly from any project directory — each `.cargo/config.toml`
already sets the target:

```bash
cd pulsardew && cargo build --release
```

## Flashing

`cargo run` flashes, resets and then streams `defmt` logs over RTT. Use this
one, because otherwise the log output has nowhere to go:

```bash
make run-pulsardew-g0b1
make run-crunchdefender-f405
make pulsardewpro-flash        # espflash, then a serial monitor
```

To flash with an ST-Link instead, which converts the ELF to a raw binary first:

```bash
make flash-pulsardew-g0b1
make flash-crunchdefender-f405
make reset
```

## Logging

The STM32 targets log through `defmt` over RTT. Formatting happens on the host,
so a log line costs a few bytes of flash and a handful of cycles on the device.
Set the level per build:

```bash
DEFMT_LOG=debug cargo run --release
```

`pulsardewpro` logs through ESP-IDF's own logger; read it with `espflash monitor`
or `make pulsardewpro-monitor`.

## Checks

```bash
make test                  # Host unit tests for the shared crate
make clippy                # Lint, warnings are errors
make clippy-pulsardewpro   # Same for the ESP32-S3 target
make fmt                   # Format every crate
```

The firmware crates are `no_std` and have no host target, so `make test` covers
the shared crate only. Anything worth unit-testing belongs there.

`make clippy` covers what the stable toolchain can build, so it still works
without espup installed. CI lints `pulsardewpro` too, since it has the Xtensa
toolchain anyway.

## Debugging

```bash
cd pulsardew
cargo embed --release          # cargo install cargo-embed
```

Or with GDB:

```bash
probe-rs gdb --chip STM32G0B1KBUx
arm-none-eabi-gdb target/thumbv6m-none-eabi/release/pulsardew
(gdb) target extended-remote :1337
```

## License

This firmware is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE)
for the full license text.
