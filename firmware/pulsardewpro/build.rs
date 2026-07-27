fn main() {
    // Hands the ESP-IDF build output (include paths, link args, sysroot) to
    // `ldproxy`, which is the linker set in .cargo/config.toml.
    embuild::espidf::sysenv::output();
}
