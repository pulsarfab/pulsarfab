#ifndef __STM32G0xx_HAL_CONF_H
#define __STM32G0xx_HAL_CONF_H

#define HAL_MODULE_ENABLED
#define HAL_ADC_MODULE_ENABLED
#define HAL_CORTEX_MODULE_ENABLED
#define HAL_DMA_MODULE_ENABLED
#define HAL_FLASH_MODULE_ENABLED
#define HAL_GPIO_MODULE_ENABLED
#define HAL_I2C_MODULE_ENABLED
#define HAL_PCD_MODULE_ENABLED
#define HAL_PWR_MODULE_ENABLED
#define HAL_RCC_MODULE_ENABLED
#define HAL_TIM_MODULE_ENABLED
#define HAL_UART_MODULE_ENABLED

#define HSE_VALUE            8000000UL
#define HSE_STARTUP_TIMEOUT  100UL
#define HSI_VALUE            16000000UL
#define HSI_STARTUP_TIMEOUT  5000UL
#define LSE_VALUE            32768UL
#define LSE_STARTUP_TIMEOUT  5000UL
#define LSI_VALUE            32000UL
#define HSI48_VALUE          48000000UL

#define VDD_VALUE            3300UL
#define TICK_INT_PRIORITY    3U
#define USE_RTOS             0U
#define PREFETCH_ENABLE      1U
#define INSTRUCTION_CACHE_ENABLE 1U

#ifdef HAL_RCC_MODULE_ENABLED
  #include "stm32g0xx_hal_rcc.h"
#endif
#ifdef HAL_GPIO_MODULE_ENABLED
  #include "stm32g0xx_hal_gpio.h"
#endif
#ifdef HAL_DMA_MODULE_ENABLED
  #include "stm32g0xx_hal_dma.h"
#endif
#ifdef HAL_CORTEX_MODULE_ENABLED
  #include "stm32g0xx_hal_cortex.h"
#endif
#ifdef HAL_ADC_MODULE_ENABLED
  #include "stm32g0xx_hal_adc.h"
  #include "stm32g0xx_hal_adc_ex.h"
#endif
#ifdef HAL_FLASH_MODULE_ENABLED
  #include "stm32g0xx_hal_flash.h"
#endif
#ifdef HAL_I2C_MODULE_ENABLED
  #include "stm32g0xx_hal_i2c.h"
  #include "stm32g0xx_hal_i2c_ex.h"
#endif
#ifdef HAL_PCD_MODULE_ENABLED
  #include "stm32g0xx_hal_pcd.h"
  #include "stm32g0xx_hal_pcd_ex.h"
#endif
#ifdef HAL_PWR_MODULE_ENABLED
  #include "stm32g0xx_hal_pwr.h"
  #include "stm32g0xx_hal_pwr_ex.h"
#endif
#ifdef HAL_TIM_MODULE_ENABLED
  #include "stm32g0xx_hal_tim.h"
  #include "stm32g0xx_hal_tim_ex.h"
#endif
#ifdef HAL_UART_MODULE_ENABLED
  #include "stm32g0xx_hal_uart.h"
  #include "stm32g0xx_hal_uart_ex.h"
#endif

#define assert_param(expr) ((void)0U)

#endif /* __STM32G0xx_HAL_CONF_H */
