# SUNMI presentation companion

This directory is for the dedicated SUNMI display companion, separate from the future Android mobile capture app in `android/`.

The first delivered slice is the [offline two-screen test](display-test/README.md). It puts a local webpage on the smaller panel while AirScreen receives Vision Pro on the larger panel. Its animations are synthetic and it remains available independently. The [new live companion](companion/README.md) adds authenticated lifecycle observation and manual display modes; see its recorded verification and remaining physical acceptance checks.

The broader architecture and delivery sequence are in [the implementation plan](../docs/SUNMI_DEMO_IMPLEMENTATION_PLAN.md).
