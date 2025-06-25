import random
import time
import subprocess

# Constants
CAN_INTERFACE = "can0"
CAN_ID = "18F00F52"  # Aftertreatment outlet sensor
SEND_INTERVAL = 0.2  # seconds between frames

def to_little_endian_bytes(value, scale, byte_count=2):
    raw = int(value / scale)
    return raw.to_bytes(byte_count, byteorder='little')

def simulate_nox_data():
    # Generate plausible values
    nox_ppm = random.uniform(10, 500)        # NOx: 10–500 ppm
    o2_percent = random.uniform(5, 15)       # O2: 5–15%

    nox_bytes = to_little_endian_bytes(nox_ppm, 0.05)     # 0.05 ppm/bit
    o2_bytes = to_little_endian_bytes(o2_percent, 0.05)   # 0.05%/bit

    status_byte = 0x00      # all good
    heater_byte = 0x00      # all good
    error_nox = 0xFF        # no error
    error_o2 = 0xFF         # no error

    payload = nox_bytes + o2_bytes + bytes([
        status_byte,
        heater_byte,
        error_nox,
        error_o2
    ])
    return payload.hex().upper()

def send_frame(data_hex):
    cmd = f"cansend {CAN_INTERFACE} {CAN_ID}#{data_hex}"
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    print("Starting NOx sensor simulation...")
    try:
        while True:
            frame = simulate_nox_data()
            send_frame(frame)
            print(f"Sent: {frame}")
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
