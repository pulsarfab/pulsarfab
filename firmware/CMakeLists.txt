cmake_minimum_required(VERSION 3.20)

# Project selection - set this via command line: -DPROJECT=pulsardew
if(NOT DEFINED PROJECT)
    message(FATAL_ERROR "PROJECT must be specified. Use -DPROJECT=pulsardew")
endif()

# MCU selection - set this via command line: -DMCU=STM32G0B1
if(NOT DEFINED MCU)
    message(FATAL_ERROR "MCU must be specified. Use -DMCU=STM32G0B1")
endif()

# Optional debug mode - set via command line: -DENABLE_DEBUG_DEFINES=ON
# Default: OFF (uses -DNDEBUG, disables assert() and debug code)
# When ON: Uses -DDEBUG instead (enables assert() and debug code)
option(ENABLE_DEBUG_DEFINES "Enable debug defines (-DDEBUG instead of -DNDEBUG)" OFF)

if(ENABLE_DEBUG_DEFINES)
    message(STATUS "Debug defines enabled: -DDEBUG (assert and debug code active)")
else()
    message(STATUS "Debug defines disabled: -DNDEBUG (assert and debug code removed)")
endif()

# Setup toolchain
set(CMAKE_TOOLCHAIN_FILE ${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi.cmake)

# Include MCU-specific settings
if(MCU STREQUAL "STM32G0B1")
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/stm32g0b1.cmake)
elseif(MCU STREQUAL "STM32G071")
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/stm32g071.cmake)
elseif(MCU STREQUAL "STM32G030")
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/stm32g030.cmake)
else()
    message(FATAL_ERROR "Unknown MCU: ${MCU}. Supported: STM32G0B1, STM32G071, STM32G030")
endif()

# Define the project
project(${PROJECT} C ASM)

# C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)

# Build common library first
add_subdirectory(common)

# Build the selected project
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT})
    add_subdirectory(${PROJECT})
else()
    message(FATAL_ERROR "Project ${PROJECT} not found")
endif()
