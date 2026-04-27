# PulsarFab

Open-source astronomy hardware platform — dew heater controllers and accessories based on STM32 and ESP32-S3 microcontrollers.

## Projects

| Project | Description | MCU | Flash/RAM | Framework | Status |
|---------|-------------|-----|-----------|-----------|--------|
| **pulsardew** | USB dew heater controller | STM32G0B1KBU6 | 128KB/144KB | STM32 HAL + FreeRTOS | 🚧 In Development |
| **pulsardewpro** | WiFi dew heater controller (ASCOM Alpaca) | ESP32-S3-MINI-1 | 8MB/512KB | ESP-IDF | 🚧 In Development |

## Repository Structure

```
pulsarfab/
├── firmware/                 # All firmware projects (C/C++, Apache 2.0)
│   ├── pulsardew/             # STM32G0B1 USB dew heater controller
│   ├── pulsardewpro/          # ESP32-S3 WiFi dew heater (ASCOM Alpaca)
│   ├── common/                # Shared STM32 HAL and utilities
│   └── shared/                # Shared protocol definitions and libraries
├── hardware/                 # PCB designs (CERN-OHL-S v2 + NC)
│   ├── pulsardew/            # USB dew heater PCB
│   ├── pulsardewpro/         # WiFi dew heater PCB
│   └── lib/                  # Shared KiCad libraries
├── mechanical/               # 3D models (coming soon, CERN-OHL-S v2 + NC)
└── LICENSE                   # Dual licensing information
```

## Quick Start

### Prerequisites

**For STM32 builds (pulsardew):**
- ARM GCC toolchain: `arm-none-eabi-gcc`
- CMake 3.20 or newer
- Make or Ninja build tool

**For ESP32-S3 builds (pulsardewpro):**
- ESP-IDF v5.x
- Python 3.10+
- uv (Python package manager)

See [firmware/README.md](firmware/README.md) for detailed installation instructions.

### Build Projects

```bash
# STM32 USB dew heater
cd firmware
make pulsardew-g0b1              # Build pulsardew (STM32G0B1)
make flash-pulsardew-g0b1        # Flash via st-flash

# ESP32-S3 WiFi dew heater
cd firmware/pulsardewpro
idf.py build                     # Build with ESP-IDF
idf.py flash                     # Flash via USB
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
- Compact STM32G0B1 design with FreeRTOS

### PulsarDewPro (WiFi / ASCOM Alpaca)
- 4 PWM heater channels with individual current sensing
- Multiple temperature/humidity sensors
- WiFi 802.11 b/g/n connectivity
- ASCOM Alpaca REST API (ObservingConditions + Switch devices)
- Web configuration UI
- OTA firmware updates
- ESP32-S3 with ESP-IDF

## Hardware

### PulsarDew (STM32G0B1KBU6)
- 128KB Flash, 144KB RAM
- ARM Cortex-M0+ @ 64MHz
- UFQFPN-32 package
- USB 2.0 FS (HSI48 + CRS, no external crystal)
- FreeRTOS real-time control

### PulsarDewPro (ESP32-S3-MINI-1)
- 8MB Flash, 512KB SRAM
- Dual-core Xtensa LX7 @ 240MHz
- WiFi 802.11 b/g/n
- USB-OTG for programming
- ASCOM Alpaca server

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
- [uv Python Package Manager](https://github.com/astral-sh/uv)

---

Copyright (c) 2025-2026 Yann Ramin
