import AcisCanTools as ACT

log = ACT.Parser(
    mode="logged", interface=ACT.utils.get_can_interface(), output_name="simTest.log", loopback=True)
log.configure_smart_nox_output()
log.beginLogging()
