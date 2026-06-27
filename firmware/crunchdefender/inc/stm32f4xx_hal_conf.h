#ifndef __STM32F4xx_HAL_CONF_H
#define __STM32F4xx_HAL_CONF_H

#define HAL_MODULE_ENABLED
#define HAL_ADC_MODULE_ENABLED
#define HAL_CORTEX_MODULE_ENABLED
#define HAL_DMA_MODULE_ENABLED
#define HAL_FLASH_MODULE_ENABLED
#define HAL_GPIO_MODULE_ENABLED
#define HAL_I2C_MODULE_ENABLED
#define HAL_PCD_MODULE_ENABLED          /* USB device (OTG_FS)        */
#define HAL_HCD_MODULE_ENABLED          /* USB host   (OTG_HS in FS)  */
#define HAL_PWR_MODULE_ENABLED
#define HAL_RCC_MODULE_ENABLED
#define HAL_TIM_MODULE_ENABLED
#define HAL_UART_MODULE_ENABLED

#define HSE_VALUE            8000000UL
#define HSE_STARTUP_TIMEOUT  100UL
#define HSI_VALUE           16000000UL
#define LSE_VALUE              32768UL
#define LSE_STARTUP_TIMEOUT  5000UL
#define LSI_VALUE              32000UL

/* Value of the I2S_CKIN external clock source. Unused on this board, but the
 * RCC HAL references it unconditionally. Value matches ST's
 * stm32f4xx_hal_conf_template.h. */
#define EXTERNAL_CLOCK_VALUE  12288000UL

#define VDD_VALUE            3300UL
#define TICK_INT_PRIORITY    0x0FU
#define USE_RTOS             0U
#define PREFETCH_ENABLE      1U
#define INSTRUCTION_CACHE_ENABLE 1U
#define DATA_CACHE_ENABLE    1U

/* USB OTG configuration */
#define USE_USB_FS                          /* OTG_FS, PA11/PA12 (device) */
#define USE_USB_HS                          /* OTG_HS, PB14/PB15           */
#define USE_USB_HS_IN_FS                    /* HS peripheral in FS PHY mode (no external ULPI) */

#ifdef HAL_RCC_MODULE_ENABLED
  #include "stm32f4xx_hal_rcc.h"
#endif
#ifdef HAL_GPIO_MODULE_ENABLED
  #include "stm32f4xx_hal_gpio.h"
#endif
#ifdef HAL_DMA_MODULE_ENABLED
  #include "stm32f4xx_hal_dma.h"
#endif
#ifdef HAL_CORTEX_MODULE_ENABLED
  #include "stm32f4xx_hal_cortex.h"
#endif
#ifdef HAL_ADC_MODULE_ENABLED
  #include "stm32f4xx_hal_adc.h"
#endif
#ifdef HAL_FLASH_MODULE_ENABLED
  #include "stm32f4xx_hal_flash.h"
#endif
#ifdef HAL_I2C_MODULE_ENABLED
  #include "stm32f4xx_hal_i2c.h"
#endif
#ifdef HAL_PCD_MODULE_ENABLED
  #include "stm32f4xx_hal_pcd.h"
#endif
#ifdef HAL_HCD_MODULE_ENABLED
  #include "stm32f4xx_hal_hcd.h"
#endif
#ifdef HAL_PWR_MODULE_ENABLED
  #include "stm32f4xx_hal_pwr.h"
#endif
#ifdef HAL_TIM_MODULE_ENABLED
  #include "stm32f4xx_hal_tim.h"
#endif
#ifdef HAL_UART_MODULE_ENABLED
  #include "stm32f4xx_hal_uart.h"
#endif

#ifdef USE_FULL_ASSERT
  void assert_failed(uint8_t *file, uint32_t line);
  #define assert_param(expr) ((expr) ? (void)0U : assert_failed((uint8_t *)__FILE__, __LINE__))
#else
  #define assert_param(expr) ((void)0U)
#endif

#endif /* __STM32F4xx_HAL_CONF_H */
