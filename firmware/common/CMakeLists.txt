# Common library with ST HAL drivers and shared utilities
#
# Each MCU family's HAL is built as its own static library. A given build
# targets exactly one MCU family, so we build only that family's HAL — gated
# on both the selected MCU_FAMILY and the presence of the corresponding
# STM32Cube vendor tree (a git submodule). Building the other family's HAL
# would fail anyway, since the per-MCU hal_conf.h include path is supplied by
# the selected project, not here. Projects link the one they need
# (stm32g0_hal, stm32f4_hal).

# ---- STM32G0 HAL ------------------------------------------------------------

set(CUBE_G0_DIR ${CMAKE_CURRENT_SOURCE_DIR}/STM32CubeG0)

if(MCU_FAMILY STREQUAL "STM32G0" AND EXISTS ${CUBE_G0_DIR})
    set(HAL_G0_DIR ${CUBE_G0_DIR}/Drivers/STM32G0xx_HAL_Driver)
    set(CMSIS_G0_DIR ${CUBE_G0_DIR}/Drivers/CMSIS)

    file(GLOB HAL_G0_SOURCES
        ${HAL_G0_DIR}/Src/stm32g0xx_hal.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_cortex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_rcc.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_rcc_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_gpio.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_dma.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_dma_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_pwr.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_pwr_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_tim.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_tim_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_uart.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_uart_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_spi.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_spi_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_i2c.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_i2c_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_adc.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_adc_ex.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_pcd.c
        ${HAL_G0_DIR}/Src/stm32g0xx_hal_pcd_ex.c
    )

    add_library(stm32g0_hal STATIC ${HAL_G0_SOURCES})

    target_include_directories(stm32g0_hal PUBLIC
        ${HAL_G0_DIR}/Inc
        ${HAL_G0_DIR}/Inc/Legacy
        ${CMSIS_G0_DIR}/Device/ST/STM32G0xx/Include
        ${CMSIS_G0_DIR}/Include
    )
endif()

# ---- STM32F4 HAL ------------------------------------------------------------

set(CUBE_F4_DIR ${CMAKE_CURRENT_SOURCE_DIR}/STM32CubeF4)

if(MCU_FAMILY STREQUAL "STM32F4" AND EXISTS ${CUBE_F4_DIR})
    set(HAL_F4_DIR ${CUBE_F4_DIR}/Drivers/STM32F4xx_HAL_Driver)
    set(CMSIS_F4_DIR ${CUBE_F4_DIR}/Drivers/CMSIS)

    file(GLOB HAL_F4_SOURCES
        ${HAL_F4_DIR}/Src/stm32f4xx_hal.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_cortex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_rcc.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_rcc_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_gpio.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_dma.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_dma_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_pwr.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_pwr_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_tim.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_tim_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_uart.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_spi.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_i2c.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_i2c_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_adc.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_adc_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_pcd.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_pcd_ex.c
        ${HAL_F4_DIR}/Src/stm32f4xx_hal_hcd.c
        ${HAL_F4_DIR}/Src/stm32f4xx_ll_usb.c
    )

    add_library(stm32f4_hal STATIC ${HAL_F4_SOURCES})

    target_include_directories(stm32f4_hal PUBLIC
        ${HAL_F4_DIR}/Inc
        ${HAL_F4_DIR}/Inc/Legacy
        ${CMSIS_F4_DIR}/Device/ST/STM32F4xx/Include
        ${CMSIS_F4_DIR}/Include
    )
endif()
