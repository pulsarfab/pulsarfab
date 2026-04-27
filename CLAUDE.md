# Claude Code Assistant Guidelines

## General Rules
- Do not run cat or stty commands
- Do not read debug messages from the serial port - ask the user to do that
- Use makefile targets when possible
- Always reset the device after flashing: `st-flash write <file> 0x08000000 --reset`

## Build Commands

### STM32 Firmware (pulsardew)
```bash
cd firmware
make pulsardew-g0b1              # Build pulsardew (STM32G0B1)
make flash-pulsardew-g0b1        # Flash via st-flash
make reset                       # Reset STM32 target
make test                        # Run unit tests
```

### ESP32-S3 Firmware (pulsardewpro)
```bash
cd firmware/pulsardewpro
idf.py build                     # Build with ESP-IDF
idf.py flash                     # Flash via USB
idf.py monitor                   # Serial monitor
idf.py flash monitor             # Flash and monitor
```

## Flashing STM32 Firmware

### Using Makefile Targets (Recommended)
```bash
cd firmware
make flash-pulsardew-g0b1        # Flash pulsardew
make reset                       # Reset STM32 target
```

### Using st-flash Directly
```bash
st-flash --reset write build/<target>/<project>/<project>.bin 0x08000000
st-flash reset  # Reset only
```

The `--reset` flag ensures the device properly resets after flashing.

## GDB Debugging (STM32)

### Standard debugging:
```bash
# Terminal 1:
st-util

# Terminal 2:
cd firmware/build
arm-none-eabi-gdb <project>.elf
(gdb) target extended-remote :4242
(gdb) load
(gdb) monitor reset
(gdb) continue
```

## ESP-IDF Debugging (ESP32-S3)

```bash
cd firmware/pulsardewpro
idf.py openocd                   # Start OpenOCD
idf.py gdb                       # Start GDB
```

## Continuous Integration

The project uses GitHub Actions for CI/CD. All builds and tests run automatically on push to main and pull requests.

### Keeping CI in Sync
**IMPORTANT**: When adding or removing firmware targets, update both:
1. `.github/workflows/build.yml` - Add CI build job
2. `firmware/Makefile` - Add build and flash targets

Both files have comments at the top reminding you to keep them synchronized.

### Running CI Locally
```bash
cd firmware
make test                        # Run unit tests
make pulsardew-g0b1              # Build STM32 pulsardew

cd firmware/pulsardewpro
idf.py build                     # Build ESP32-S3 pulsardewpro
```
