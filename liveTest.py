import AcisCanTools as ACT

log = ACT.Logger(mode="stream")

while True:
    packet = log.read(timeout=1)
    data = ACT.utils.static_decode(packet.data)
    print(f"SRC: {packet.arbitration_id & 0xFF}")
    print(f"PGN: {(packet.arbitration_id >> 8) & 0x3FFFF}")
    print(f"NOx: {((data[0] * .05) - 200):.2f}PPM")
    print(f"O2: {((data[1] * .000514) - 12):.2f}%")
    print("")
    
