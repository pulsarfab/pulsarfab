//! CrunchDefender — Skywatcher mount limit guard (STM32F405RGT6).

#![no_std]
#![no_main]

use defmt::info;
use embassy_executor::Spawner;
use embassy_stm32::Config;
use embassy_time::{Duration, Timer};

use {defmt_rtt as _, panic_probe as _};

mod clock;

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let mut config = Config::default();
    clock::configure(&mut config);
    let _p = embassy_stm32::init(config);

    info!("crunchdefender up, sysclk {} Hz", clock::SYSCLK_HZ);

    loop {
        Timer::after(Duration::from_millis(500)).await;
    }
}
