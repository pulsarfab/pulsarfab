# Claude Code Assistant Guidelines

## General Rules
- Do not run cat or stty commands
- Do not read debug messages from the serial port - ask the user to do that
- Use makefile targets when possible
- All firmware is Rust: Embassy on the STM32 targets, `esp-idf-svc` on the ESP32-S3

## Build Commands

Every target is a separate cargo package under `firmware/`. Each has its own
`.cargo/config.toml` that already sets the Rust target, so plain `cargo build`
works from inside a project directory.

### STM32 Firmware (pulsardew, STM32G0B1 / thumbv6m-none-eabi)
```bash
cd firmware
make pulsardew-g0b1              # Build
make run-pulsardew-g0b1          # Flash via probe-rs, reset, stream defmt logs
make flash-pulsardew-g0b1        # Flash via st-flash instead
make reset                       # Reset STM32 target
```

### STM32 Firmware (crunchdefender, STM32F405 / thumbv7em-none-eabihf)
```bash
cd firmware
make crunchdefender-f405         # Build
make run-crunchdefender-f405     # Flash via probe-rs, reset, stream defmt logs
make flash-crunchdefender-f405   # Flash via st-flash instead
```

### ESP32-S3 Firmware (pulsardewpro, xtensa-esp32s3-espidf)
```bash
cd firmware
make pulsardewpro                # Build
make pulsardewpro-flash          # Flash via espflash and monitor
make pulsardewpro-monitor        # Serial monitor only
```

Xtensa is not an upstream Rust target. This needs Espressif's Rust fork,
installed with `cargo install espup && espup install`, then
`source ~/export-esp.sh`. `pulsardewpro/rust-toolchain.toml` selects it.

### Checks
```bash
cd firmware
make test                        # Host unit tests (shared crate only)
make clippy                      # Lint every target, warnings are errors
make fmt                         # Format every crate
```

## Flashing STM32 Firmware

### Using Makefile Targets (Recommended)
`make run-*` is the one to reach for: probe-rs flashes, resets, and then streams
`defmt` logs over RTT. Without it the log output has nowhere to go.

```bash
cd firmware
make run-pulsardew-g0b1
```

### Using st-flash Directly
Cargo emits an ELF, so convert it first:

```bash
arm-none-eabi-objcopy -O binary <elf> <elf>.bin
st-flash --reset write <elf>.bin 0x08000000
st-flash reset  # Reset only
```

The `--reset` flag ensures the device properly resets after flashing.

## Debugging (STM32)

```bash
cd firmware/pulsardew
cargo embed --release            # cargo install cargo-embed
```

Or with GDB:
```bash
# Terminal 1:
probe-rs gdb --chip STM32G0B1KBUx

# Terminal 2:
cd firmware/pulsardew
arm-none-eabi-gdb target/thumbv6m-none-eabi/release/pulsardew
(gdb) target extended-remote :1337
(gdb) continue
```

## Writing Firmware Code

- Anything worth unit-testing goes in `firmware/shared` (`pulsarfab-shared`).
  It is `no_std` and free of hardware access, so it builds for every target and
  runs on the host under `cargo test`. The firmware crates have no host target.
- Log with `defmt` on STM32 and the `log` crate on ESP32-S3. `defmt` formats on
  the host, so log lines are nearly free in flash. Set the level with
  `DEFMT_LOG=debug`.
- Clock setup lives in each project's `src/clock.rs`.
- There are no linker scripts or startup files to maintain: `embassy-stm32`'s
  `memory-x` feature generates the memory map and `cortex-m-rt` supplies the
  vector table.

## Continuous Integration

The project uses GitHub Actions for CI/CD. All builds and tests run automatically on push to main and pull requests.

### Keeping CI in Sync
**IMPORTANT**: When adding or removing firmware targets, update both:
1. `.github/workflows/build.yml` - Add CI build job
2. `firmware/Makefile` - Add build and flash targets

Both files have comments at the top reminding you to keep them synchronized.

CI runs `cargo fmt --check` and `cargo clippy -- -D warnings` on every target,
so run `make fmt` and `make clippy` before pushing.

### Running CI Locally
```bash
cd firmware
make test                        # Host unit tests
make clippy                      # Lint
make pulsardew-g0b1              # Build STM32 pulsardew
make crunchdefender-f405         # Build STM32 crunchdefender
make pulsardewpro                # Build ESP32-S3 pulsardewpro
```
