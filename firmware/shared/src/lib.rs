//! Code shared by every PulsarFab firmware target.
//!
//! Builds for both bare-metal targets and the host, so everything here stays
//! `no_std` and free of hardware access. Unit tests run on the host with
//! `cargo test`.

#![cfg_attr(not(test), no_std)]

pub mod dewpoint;

pub use dewpoint::{dew_point_c, relative_humidity_at};
