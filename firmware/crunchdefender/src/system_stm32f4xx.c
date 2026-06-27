/*
 * Minimal system_stm32f4xx.c — sets up the SystemCoreClock variable that the
 * HAL needs to compute baud rates and tick periods. The real clock tree is
 * configured later in SystemClock_Config() (main.c) using HAL_RCC_OscConfig
 * and HAL_RCC_ClockConfig.
 *
 * Replace with the version from STM32CubeF4/Drivers/CMSIS/Device/ST/STM32F4xx/
 * Source/Templates/system_stm32f4xx.c once the submodule is in place if a
 * fuller implementation is needed.
 */

#include "stm32f4xx.h"

#if !defined(HSE_VALUE)
#define HSE_VALUE    8000000U
#endif
#if !defined(HSI_VALUE)
#define HSI_VALUE   16000000U
#endif

#define VECT_TAB_OFFSET  0x00U

uint32_t SystemCoreClock = 16000000U;

const uint8_t AHBPrescTable[16] = {0,0,0,0,0,0,0,0,1,2,3,4,6,7,8,9};
const uint8_t APBPrescTable[8]  = {0,0,0,0,1,2,3,4};

void SystemInit(void)
{
    /* FPU enable: full access on CP10 and CP11 */
#if (__FPU_PRESENT == 1) && (__FPU_USED == 1)
    SCB->CPACR |= ((3UL << 10*2) | (3UL << 11*2));
#endif

    /* Reset RCC clock configuration to default reset state */
    RCC->CR    |= 0x00000001U;            /* HSION */
    RCC->CFGR   = 0x00000000U;
    RCC->CR    &= 0xFEF6FFFFU;            /* HSEON, CSSON, PLLON off */
    RCC->PLLCFGR = 0x24003010U;
    RCC->CR    &= 0xFFFBFFFFU;            /* HSEBYP off */
    RCC->CIR    = 0x00000000U;

    SCB->VTOR = FLASH_BASE | VECT_TAB_OFFSET;
}

void SystemCoreClockUpdate(void)
{
    uint32_t sysclock, pllm, pllvco, pllp;
    uint32_t cfgr = RCC->CFGR;

    switch (cfgr & RCC_CFGR_SWS) {
        case RCC_CFGR_SWS_HSI: sysclock = HSI_VALUE; break;
        case RCC_CFGR_SWS_HSE: sysclock = HSE_VALUE; break;
        case RCC_CFGR_SWS_PLL: {
            pllm = RCC->PLLCFGR & RCC_PLLCFGR_PLLM;
            if ((RCC->PLLCFGR & RCC_PLLCFGR_PLLSRC) != 0)
                pllvco = (HSE_VALUE / pllm) * ((RCC->PLLCFGR & RCC_PLLCFGR_PLLN) >> 6);
            else
                pllvco = (HSI_VALUE / pllm) * ((RCC->PLLCFGR & RCC_PLLCFGR_PLLN) >> 6);
            pllp = (((RCC->PLLCFGR & RCC_PLLCFGR_PLLP) >> 16) + 1) * 2;
            sysclock = pllvco / pllp;
            break;
        }
        default: sysclock = HSI_VALUE; break;
    }

    SystemCoreClock = sysclock >> AHBPrescTable[(cfgr & RCC_CFGR_HPRE) >> 4];
}
