# PulsarFab

Open-source astronomy hardware platform — dew heater controllers, mount accessories, and other observatory gear based on STM32 and ESP32-S3 microcontrollers.

## Projects

| Project | Description | MCU | Flash/RAM | Framework | Status |
|---------|-------------|-----|-----------|-----------|--------|
| **pulsardew** | USB dew heater controller | STM32G0B1KBU6 | 128KB/144KB | Rust + Embassy | 🚧 In Development |
| **pulsardewpro** | WiFi dew heater controller (ASCOM Alpaca) | ESP32-S3-MINI-1 | 8MB/512KB | Rust + esp-idf-svc | 🚧 In Development |
| **crunchdefender** | Skywatcher mount limit guard — inline USB host/device that interrupts motion before the OTA collides with the pier or cables crunch | STM32F405RGT6 | 1024KB/192KB | Rust + Embassy | 🌱 Bootstrapped |

## Repository Structure

```
pulsarfab/
├── firmware/                 # All firmware projects (Rust, Apache 2.0)
│   ├── pulsardew/             # STM32G0B1 USB dew heater controller
│   ├── pulsardewpro/          # ESP32-S3 WiFi dew heater (ASCOM Alpaca)
│   ├── crunchdefender/        # STM32F405 mount limit guard (dual-USB)
│   └── shared/                # pulsarfab-shared: code common to all targets
├── hardware/                 # PCB designs (CERN-OHL-S v2 + NC)
│   ├── pulsardew/            # USB dew heater PCB
│   ├── pulsardewpro/         # WiFi dew heater PCB
│   ├── crunchdefender/       # Mount limit guard PCB
│   └── lib/                  # Shared KiCad libraries
├── mechanical/               # 3D models (coming soon, CERN-OHL-S v2 + NC)
└── LICENSE                   # Dual licensing information
```

## Quick Start

### Prerequisites

**For STM32 builds (pulsardew, crunchdefender):**
- Rust, via [rustup](https://rustup.rs) — `rust-toolchain.toml` does the rest
- `probe-rs`, to flash and to read `defmt` logs: `cargo install probe-rs-tools`
- ARM binutils, for `arm-none-eabi-size` and `-objcopy`

**For ESP32-S3 builds (pulsardewpro):**
- Espressif's Rust fork: `cargo install espup && espup install`
- `cargo install ldproxy espflash`
- Python 3.10+

See [firmware/README.md](firmware/README.md) for detailed installation instructions.

### Build Projects

```bash
# STM32 USB dew heater
cd firmware
make pulsardew-g0b1              # Build pulsardew (STM32G0B1)
make run-pulsardew-g0b1          # Flash and stream defmt logs

# STM32 mount limit guard
cd firmware
make crunchdefender-f405         # Build crunchdefender (STM32F405)
make run-crunchdefender-f405     # Flash and stream defmt logs

# ESP32-S3 WiFi dew heater
cd firmware
make pulsardewpro                # Build pulsardewpro (ESP32-S3)
make pulsardewpro-flash          # Flash and monitor
```

## Key Features

### Dew Heater Control
- PWM-controlled heater outputs for telescope optics
- Temperature and humidity sensing (SHT40)
- Ambient dew point calculation with automatic heater regulation
- Configurable temperature setpoints per channel

### PulsarDew (USB)
- 4 PWM heater channels with current sensing
- Temperature/humidity sensor (SHT40 via I2C)
- USB 2.0 FS device (CDC for serial control from PC)
- Dew point calculation and automatic regulation
- Compact STM32G0B1 design, async control with Embassy

### PulsarDewPro (WiFi / ASCOM Alpaca)
- 4 PWM heater channels with individual current sensing
- Multiple temperature/humidity sensors
- WiFi 802.11 b/g/n connectivity
- ASCOM Alpaca REST API (ObservingConditions + Switch devices)
- Web configuration UI
- OTA firmware updates
- ESP32-S3, Rust on ESP-IDF

## Hardware

### PulsarDew (STM32G0B1KBU6)
- 128KB Flash, 144KB RAM
- ARM Cortex-M0+ @ 64MHz
- UFQFPN-32 package
- USB 2.0 FS (HSI48 + CRS, no external crystal)
- Async control with Embassy

### PulsarDewPro (ESP32-S3-MINI-1)
- 8MB Flash, 512KB SRAM
- Dual-core Xtensa LX7 @ 240MHz
- WiFi 802.11 b/g/n
- USB-OTG for programming
- ASCOM Alpaca server

### CrunchDefender (STM32F405RGT6)
- 1024KB Flash, 192KB RAM (128KB SRAM + 64KB CCM)
- ARM Cortex-M4F @ 168MHz with single-precision FPU
- LQFP-64 package
- **Two USB peripherals running concurrently** — OTG_FS as device (PA11/PA12) to the host PC, OTG_HS-in-FS-mode as host (PB14/PB15) to the Skywatcher hand controller
- Sits inline on the USB link, parses position telemetry, intercepts motion commands when limits are exceeded

## License

This project uses dual licensing:

- **Firmware/Software**: [Apache 2.0](firmware/LICENSE)
- **Hardware Designs**: CERN-OHL-S v2 (strongly reciprocal) + Non-Commercial restriction

See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please ensure:
- Firmware contributions follow the Apache 2.0 license
- Hardware contributions follow CERN-OHL-S v2 + NC
- Code follows the existing style
- All changes are tested

## Resources

### Hardware
- [STM32G0 Series](https://www.st.com/en/microcontrollers-microprocessors/stm32g0-series.html)
- [ESP-IDF Documentation](https://docs.espressif.com/projects/esp-idf/)
- [ASCOM Alpaca](https://ascom-standards.org/Developer/Alpaca.htm)

### Licenses
- [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)
- [CERN-OHL-S v2](https://ohwr.org/cern_ohl_s_v2.txt)

### Tools
- [Embassy](https://embassy.dev) — async embedded Rust
- [esp-rs](https://github.com/esp-rs) — Rust on Espressif chips
- [probe-rs](https://probe.rs) — flashing and debugging

---

Copyright (c) 2025-2026 Yann Ramin
