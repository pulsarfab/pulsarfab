//! Clock tree: 16 MHz HSI -> PLL -> 64 MHz SYSCLK.
//!
//! HSI/1 = 16 MHz into the PLL, x8 = 128 MHz VCO, /2 on R = 64 MHz, the G0's
//! ceiling. USB runs off HSI48 trimmed by the CRS against the USB SOF frames —
//! a 128 MHz VCO cannot divide down to 48 MHz, so the PLL cannot feed it.

use embassy_stm32::rcc::{
    AHBPrescaler, APBPrescaler, Hsi, HsiSysDiv, Pll, PllPreDiv, PllRDiv, PllSource, Sysclk,
};
use embassy_stm32::Config;

/// Resulting core clock. Logged at boot and used to size anything that counts
/// in core cycles.
pub const SYSCLK_HZ: u32 = 64_000_000;

pub fn configure(config: &mut Config) {
    config.rcc.hsi = Some(Hsi {
        sys_div: HsiSysDiv::DIV1,
    });
    config.rcc.pll = Some(Pll {
        source: PllSource::HSI,
        prediv: PllPreDiv::DIV1,
        mul: embassy_stm32::rcc::PllMul::MUL8,
        divp: None,
        divq: None,
        divr: Some(PllRDiv::DIV2),
    });
    config.rcc.sys = Sysclk::PLL1_R;
    config.rcc.ahb_pre = AHBPrescaler::DIV1;
    config.rcc.apb1_pre = APBPrescaler::DIV1;
}
