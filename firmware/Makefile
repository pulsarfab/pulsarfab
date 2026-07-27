# Makefile for PulsarFab Firmware Projects
# Wraps cargo for the three firmware targets.
#
# IMPORTANT: Keep targets in sync with .github/workflows/build.yml!
# When adding/removing firmware targets, update both:
# - firmware/Makefile (this file)
# - .github/workflows/build.yml (CI builds)

.PHONY: help clean test fmt clippy clippy-pulsardewpro reset
.PHONY: pulsardew-g0b1 flash-pulsardew-g0b1 run-pulsardew-g0b1
.PHONY: crunchdefender-f405 flash-crunchdefender-f405 run-crunchdefender-f405
.PHONY: pulsardewpro pulsardewpro-flash pulsardewpro-monitor

# Where cargo drops each release binary. Cargo emits an ELF with no suffix.
PULSARDEW_ELF       := pulsardew/target/thumbv6m-none-eabi/release/pulsardew
CRUNCHDEFENDER_ELF  := crunchdefender/target/thumbv7em-none-eabihf/release/crunchdefender

help:
	@echo "PulsarFab Firmware Build System"
	@echo ""
	@echo "STM32 Build Targets (cargo + embassy):"
	@echo "  pulsardew-g0b1            Build pulsardew for STM32G0B1"
	@echo "  crunchdefender-f405       Build crunchdefender for STM32F405"
	@echo ""
	@echo "STM32 Flash Targets:"
	@echo "  run-pulsardew-g0b1        Flash via probe-rs and stream defmt logs"
	@echo "  run-crunchdefender-f405   Flash via probe-rs and stream defmt logs"
	@echo "  flash-pulsardew-g0b1      Flash via st-flash"
	@echo "  flash-crunchdefender-f405 Flash via st-flash"
	@echo "  reset                     Reset STM32 target"
	@echo ""
	@echo "ESP32-S3 Projects (esp-idf-svc, needs the espup 'esp' toolchain):"
	@echo "  pulsardewpro              Build pulsardewpro (ESP32-S3)"
	@echo "  pulsardewpro-flash        Flash and monitor pulsardewpro"
	@echo "  pulsardewpro-monitor      Monitor pulsardewpro serial output"
	@echo ""
	@echo "Checks:"
	@echo "  test                      Run host unit tests"
	@echo "  clippy                    Lint every target"
	@echo "  fmt                       Format every crate"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean                     Clean all build artifacts"

# ---------------------------------------------------------------- STM32 build

pulsardew-g0b1:
	@echo "Building pulsardew for STM32G0B1..."
	@cd pulsardew && cargo build --release
	@arm-none-eabi-size $(PULSARDEW_ELF)

crunchdefender-f405:
	@echo "Building crunchdefender for STM32F405..."
	@cd crunchdefender && cargo build --release
	@arm-none-eabi-size $(CRUNCHDEFENDER_ELF)

# ---------------------------------------------------------------- STM32 flash

# probe-rs flashes, resets and then streams defmt logs over RTT. Preferred:
# without it the defmt output has nowhere to go.
run-pulsardew-g0b1:
	@cd pulsardew && cargo run --release

run-crunchdefender-f405:
	@cd crunchdefender && cargo run --release

# st-flash needs a raw binary, which cargo does not produce on its own.
flash-pulsardew-g0b1: pulsardew-g0b1
	@arm-none-eabi-objcopy -O binary $(PULSARDEW_ELF) $(PULSARDEW_ELF).bin
	st-flash --reset write $(PULSARDEW_ELF).bin 0x08000000

flash-crunchdefender-f405: crunchdefender-f405
	@arm-none-eabi-objcopy -O binary $(CRUNCHDEFENDER_ELF) $(CRUNCHDEFENDER_ELF).bin
	st-flash --reset write $(CRUNCHDEFENDER_ELF).bin 0x08000000

reset:
	@echo "Resetting STM32 target..."
	st-flash reset

# ------------------------------------------------------------------- ESP32-S3

pulsardewpro:
	@echo "Building pulsardewpro (ESP32-S3)..."
	@cd pulsardewpro && cargo build --release

pulsardewpro-flash:
	@cd pulsardewpro && cargo run --release

pulsardewpro-monitor:
	@cd pulsardewpro && espflash monitor

# --------------------------------------------------------------------- checks

# Only the shared crate runs on the host; the firmware crates are no_std and
# have no host target to test against.
test:
	@cd shared && cargo test

# Covers everything buildable with the stable toolchain, so a contributor
# without espup can still run it. CI lints pulsardewpro as well.
clippy:
	@cd shared && cargo clippy --all-targets -- -D warnings
	@cd pulsardew && cargo clippy --release -- -D warnings
	@cd crunchdefender && cargo clippy --release -- -D warnings

clippy-pulsardewpro:
	@cd pulsardewpro && cargo clippy --release -- -D warnings

fmt:
	@cd shared && cargo fmt
	@cd pulsardew && cargo fmt
	@cd crunchdefender && cargo fmt
	@# rustfmt needs no code generation, so use stable here rather than make
	@# formatting depend on having the espup toolchain installed.
	@cd pulsardewpro && cargo +stable fmt

clean:
	@echo "Cleaning all build artifacts..."
	@cd shared && cargo clean
	@cd pulsardew && cargo clean
	@cd crunchdefender && cargo clean
	@cd pulsardewpro && cargo clean
	@echo "Clean complete!"
