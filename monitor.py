import AcisCanTools as ACT
from AcisCanTools import utils as u

log = ACT.Logger(mode="stream", interface=u.get_can_interface())

while True:
    try:
        packet = log.read(timeout=1)
        data = packet.data
        arbitration_id = packet.arbitration_id
        src = u.extract_arbitration_field(arbitration_id, 'src')
        pgn = u.extract_arbitration_field(arbitration_id, 'pgn')
        nox = u.extract_data_field(data, 'nox', convert_raw=True)
        o2 = u.extract_data_field(data, 'o2', convert_raw=True)
        if src != 0:  # Src filtering is unreliable and PGN should be used instead but it's simpler for this isolated test case
            print(f"SRC: {src}")
            print(f"PGN: {pgn}")
            print(f"NOx: {nox:.2f}PPM")
            print(f"02: {o2:.2f}%")
            print("")
    except KeyboardInterrupt:
        print("\nExiting monitor.")
        log.bus.shutdown()
        break
