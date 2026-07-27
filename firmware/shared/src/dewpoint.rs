//! Dew point from temperature and relative humidity.
//!
//! Uses the Magnus-Tetens approximation with the Sonntag coefficients, good to
//! about ±0.35 °C over -45..60 °C — well inside the SHT40's own error band.

use libm::{expf, logf};

/// Magnus coefficient `a`, dimensionless.
const A: f32 = 17.62;
/// Magnus coefficient `b`, in degrees Celsius.
const B: f32 = 243.12;

/// Dew point in °C for an air temperature in °C and a relative humidity in
/// percent.
///
/// Humidity is clamped to 0.01..100 %; a reading of exactly zero has no dew
/// point, and sensors do occasionally report slightly over 100 %.
pub fn dew_point_c(temperature_c: f32, relative_humidity_pct: f32) -> f32 {
    let rh = relative_humidity_pct.clamp(0.01, 100.0);
    let gamma = (A * temperature_c) / (B + temperature_c) + logf(rh / 100.0);
    (B * gamma) / (A - gamma)
}

/// Relative humidity in percent that a given dew point implies at a given air
/// temperature. The inverse of [`dew_point_c`].
pub fn relative_humidity_at(temperature_c: f32, dew_point_c: f32) -> f32 {
    let numerator = expf((A * dew_point_c) / (B + dew_point_c));
    let denominator = expf((A * temperature_c) / (B + temperature_c));
    (100.0 * numerator / denominator).clamp(0.0, 100.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn close(a: f32, b: f32, tolerance: f32) {
        assert!(
            (a - b).abs() <= tolerance,
            "{a} != {b} (tolerance {tolerance})"
        );
    }

    #[test]
    fn saturated_air_dews_at_its_own_temperature() {
        close(dew_point_c(20.0, 100.0), 20.0, 0.01);
        close(dew_point_c(-5.0, 100.0), -5.0, 0.01);
    }

    #[test]
    fn matches_published_values() {
        // 20 °C / 50 % RH is 9.3 °C by the standard psychrometric tables.
        close(dew_point_c(20.0, 50.0), 9.3, 0.1);
        // A cold clear night: 5 °C / 80 % RH.
        close(dew_point_c(5.0, 80.0), 1.9, 0.1);
    }

    #[test]
    fn dew_point_never_exceeds_air_temperature() {
        for t in -40..=60 {
            for rh in 1..=100 {
                let dp = dew_point_c(t as f32, rh as f32);
                assert!(dp <= t as f32 + 0.01, "t={t} rh={rh} dp={dp}");
            }
        }
    }

    #[test]
    fn humidity_round_trips_through_dew_point() {
        for t in [-10.0f32, 0.0, 15.0, 30.0] {
            for rh in [10.0f32, 45.0, 90.0] {
                close(relative_humidity_at(t, dew_point_c(t, rh)), rh, 0.1);
            }
        }
    }

    #[test]
    fn zero_humidity_does_not_produce_nan() {
        assert!(dew_point_c(20.0, 0.0).is_finite());
    }
}
