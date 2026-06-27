#include "stm32g0xx.h"

uint32_t SystemCoreClock = 64000000UL;
/* uint32_t to match the extern declarations in the CMSIS G0 device header
 * (system_stm32g0xx.h); the F4 CMSIS headers declare these as uint8_t. */
const uint32_t AHBPrescTable[16] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 6, 7, 8, 9};
const uint32_t APBPrescTable[8] = {0, 0, 0, 0, 1, 2, 3, 4};

void SystemInit(void)
{
}
