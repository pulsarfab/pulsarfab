# PulsarFab Firmware

Firmware for PulsarFab dew heater controllers — STM32G0 (USB) and ESP32-S3 (WiFi/ASCOM Alpaca).

## Projects

| Project | MCU | Flash | RAM | Package | Framework | Status |
|---------|-----|-------|-----|---------|-----------|--------|
| **pulsardew** | STM32G0B1KBU6 | 128KB | 144KB | UFQFPN-32 | STM32 HAL + FreeRTOS | 🚧 Development |
| **pulsardewpro** | ESP32-S3-MINI-1 | 8MB | 512KB | Module | ESP-IDF | 🚧 Development |

## Project Structure

```
firmware/
├── CMakeLists.txt              # Top-level build configuration (STM32 only)
├── Makefile                    # Convenience build/flash targets
├── cmake/                      # Build system configuration (STM32)
│   ├── arm-none-eabi.cmake    # ARM GCC toolchain
│   ├── stm32g0b1.cmake       # STM32G0B1 MCU configuration
│   ├── stm32g071.cmake       # STM32G071 MCU configuration
│   └── stm32g030.cmake       # STM32G030 MCU configuration
├── common/                     # Shared STM32 libraries and code
│   ├── CMakeLists.txt         # Common library build config
│   └── STM32CubeG0/           # ST HAL/LL drivers (submodule)
├── shared/                     # Shared code between projects
├── pulsardew/                  # STM32G0B1 USB dew heater
│   ├── src/                   # Source files
│   ├── inc/                   # Header files
│   ├── startup/               # Startup assembly
│   ├── linker/                # Linker scripts
│   └── CMakeLists.txt         # Project build config
└── pulsardewpro/               # ESP32-S3 WiFi dew heater (ESP-IDF)
    ├── main/                  # Main application source
    ├── components/            # Custom ESP-IDF components
    ├── CMakeLists.txt         # ESP-IDF project file
    └── sdkconfig.defaults     # ESP-IDF configuration defaults
```

## Prerequisites

### For STM32 Builds (pulsardew)

1. **ARM GCC Toolchain**: `arm-none-eabi-gcc`
   - macOS: `brew install --cask gcc-arm-embedded`
   - Ubuntu/Debian: `sudo apt install gcc-arm-none-eabi`

2. **CMake**: Version 3.20 or newer

3. **Build tools**: `make` or `ninja`

4. **st-flash**: For flashing via ST-Link
   - macOS: `brew install stlink`

### For ESP32-S3 Builds (pulsardewpro)

1. **ESP-IDF**: Version 5.x
   - Follow [ESP-IDF Getting Started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/)

2. **Python 3.10+** with **uv**

## Building

### PulsarDew (STM32G0B1)

```bash
# Using Makefile targets (recommended)
make pulsardew-g0b1
make flash-pulsardew-g0b1

# Or manually with CMake
mkdir -p build/pulsardew-g0b1
cd build/pulsardew-g0b1
cmake ../.. -DPROJECT=pulsardew -DMCU=STM32G0B1 -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

### PulsarDewPro (ESP32-S3)

```bash
cd pulsardewpro
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

## License

This firmware is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for the full license text.

Copyright (c) 2025-2026 Yann Ramin
