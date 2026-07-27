fn main() {
    // embassy-stm32's `memory-x` feature emits the linker memory map for us,
    // so all we need to do is re-run when the linker invocation changes.
    println!("cargo:rustc-link-arg-bins=--nmagic");
    println!("cargo:rerun-if-changed=build.rs");
}
