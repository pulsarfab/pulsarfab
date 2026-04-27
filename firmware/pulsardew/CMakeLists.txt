# PulsarDew - STM32G0B1 USB Dew Heater Controller

set(PROJECT_SOURCES
    src/main.c
    src/system_stm32g0xx.c
)

set(STARTUP_SOURCES
    startup/startup_stm32g0b1xx.s
)

# Executable
add_executable(${PROJECT_NAME}
    ${PROJECT_SOURCES}
    ${STARTUP_SOURCES}
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    inc
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    stm32g0_hal
)

# HAL configuration header is in this project's inc/
target_include_directories(stm32g0_hal PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/inc
)

# Linker script
set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/linker/STM32G0B1KBUx_FLASH.ld)
target_link_options(${PROJECT_NAME} PRIVATE
    -T${LINKER_SCRIPT}
    -Wl,-Map=${PROJECT_NAME}.map
)

# Generate .hex and .bin files
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>
    COMMENT "Generating .hex and .bin files"
)
