# Makefile for PulsarFab Firmware Projects
# Provides convenient targets for building STM32 and ESP32-S3 projects
#
# IMPORTANT: Keep targets in sync with .github/workflows/build.yml!
# When adding/removing firmware targets, update both:
# - firmware/Makefile (this file)
# - .github/workflows/build.yml (CI builds)

.PHONY: help clean test reset
.PHONY: pulsardew-g0b1
.PHONY: flash-pulsardew-g0b1
.PHONY: pulsardewpro pulsardewpro-flash pulsardewpro-monitor

# Default target
help:
	@echo "PulsarFab Firmware Build System"
	@echo ""
	@echo "STM32 Build Targets (using CMake + arm-none-eabi-gcc):"
	@echo "  pulsardew-g0b1          Build pulsardew for STM32G0B1"
	@echo ""
	@echo "STM32 Flash Targets (using st-flash):"
	@echo "  flash-pulsardew-g0b1    Flash pulsardew"
	@echo "  reset                   Reset STM32 target"
	@echo ""
	@echo "ESP32-S3 Projects (using ESP-IDF):"
	@echo "  pulsardewpro            Build pulsardewpro (ESP32-S3)"
	@echo "  pulsardewpro-flash      Flash pulsardewpro"
	@echo "  pulsardewpro-monitor    Monitor pulsardewpro serial output"
	@echo ""
	@echo "Testing:"
	@echo "  test                    Run unit tests"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean                   Clean all build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make pulsardew-g0b1                         # Build STM32 firmware"
	@echo "  make flash-pulsardew-g0b1                   # Flash STM32 firmware"
	@echo "  make pulsardewpro                            # Build ESP32-S3 firmware"

# STM32 Projects
pulsardew-g0b1:
	@echo "Building pulsardew for STM32G0B1..."
	@mkdir -p build/pulsardew-g0b1
	@cd build/pulsardew-g0b1 && \
		cmake ../.. -DPROJECT=pulsardew -DMCU=STM32G0B1 -DCMAKE_BUILD_TYPE=Release && \
		make -j$$(nproc)
	@echo "Build complete: build/pulsardew-g0b1/pulsardew.elf"

# STM32 Flash Targets
flash-pulsardew-g0b1:
	@echo "Flashing pulsardew for STM32G0B1..."
	st-flash --reset write build/pulsardew-g0b1/pulsardew/pulsardew.bin 0x08000000

# Reset STM32 target
reset:
	@echo "Resetting STM32 target..."
	st-flash reset

# ESP32-S3 Projects
pulsardewpro:
	@echo "Building pulsardewpro (ESP32-S3)..."
	@cd pulsardewpro && idf.py build

pulsardewpro-flash:
	@echo "Flashing pulsardewpro..."
	@cd pulsardewpro && idf.py flash

pulsardewpro-monitor:
	@echo "Monitoring pulsardewpro..."
	@cd pulsardewpro && idf.py monitor

# Testing
test:
	@echo "Running unit tests..."
	@echo "No tests configured yet."

# Cleaning
clean:
	@echo "Cleaning all build artifacts..."
	@rm -rf build/
	@cd pulsardewpro && idf.py fullclean 2>/dev/null || true
	@echo "Clean complete!"

clean-pulsardew-g0b1:
	@rm -rf build/pulsardew-g0b1
