//! PulsarDewPro — WiFi dew heater controller, ASCOM Alpaca (ESP32-S3-MINI-1).

use esp_idf_svc::hal::delay::FreeRtos;
use esp_idf_svc::log::EspLogger;
use esp_idf_svc::sys::{self, EspError};

fn main() -> Result<(), EspError> {
    // Pulls in the runtime patches that ESP-IDF expects but that the linker
    // would otherwise drop, since nothing in Rust references them.
    sys::link_patches();
    EspLogger::initialize_default();

    init_nvs()?;

    log::info!("PulsarDewPro starting...");

    loop {
        FreeRtos::delay_ms(1000);
    }
}

/// Bring up the default NVS partition, wiping it if the on-flash layout is
/// stale or full. Losing stored settings beats refusing to boot.
fn init_nvs() -> Result<(), EspError> {
    let ret = unsafe { sys::nvs_flash_init() };
    if ret == sys::ESP_ERR_NVS_NO_FREE_PAGES || ret == sys::ESP_ERR_NVS_NEW_VERSION_FOUND {
        log::warn!("NVS partition unusable (error {ret}), erasing");
        esp_idf_svc::sys::esp!(unsafe { sys::nvs_flash_erase() })?;
        esp_idf_svc::sys::esp!(unsafe { sys::nvs_flash_init() })?;
        return Ok(());
    }
    esp_idf_svc::sys::esp!(ret)?;
    Ok(())
}
