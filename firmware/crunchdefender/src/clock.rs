//! Clock tree: 8 MHz HSE -> PLL -> 168 MHz SYSCLK, 48 MHz for USB.
//!
//! HSE/8 = 1 MHz into the PLL, x336 = 336 MHz VCO, /2 on P = 168 MHz SYSCLK,
//! /7 on Q = 48 MHz for the two USB peripherals. AHB runs at the full 168 MHz;
//! APB1 is capped at 42 MHz and APB2 at 84 MHz, so they divide by 4 and 2.

use embassy_stm32::rcc::{
    AHBPrescaler, APBPrescaler, Hse, HseMode, Pll, PllMul, PllPDiv, PllPreDiv, PllQDiv, PllSource,
    Sysclk,
};
use embassy_stm32::time::Hertz;
use embassy_stm32::Config;

/// Resulting core clock. Logged at boot and used to size anything that counts
/// in core cycles.
pub const SYSCLK_HZ: u32 = 168_000_000;

pub fn configure(config: &mut Config) {
    config.rcc.hse = Some(Hse {
        freq: Hertz(8_000_000),
        mode: HseMode::Oscillator,
    });
    config.rcc.pll_src = PllSource::HSE;
    config.rcc.pll = Some(Pll {
        prediv: PllPreDiv::DIV8,
        mul: PllMul::MUL336,
        divp: Some(PllPDiv::DIV2),
        divq: Some(PllQDiv::DIV7),
        divr: None,
    });
    config.rcc.sys = Sysclk::PLL1_P;
    config.rcc.ahb_pre = AHBPrescaler::DIV1;
    config.rcc.apb1_pre = APBPrescaler::DIV4;
    config.rcc.apb2_pre = APBPrescaler::DIV2;
}
