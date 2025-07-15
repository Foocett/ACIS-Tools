import AcisCanTools as ACT
import os

fileName = input("Input the desired file name: ")
fileLocation = input(
    "Input output location (leave blank for current directory): ")

# Format the output location properly
if fileLocation.strip():
    # Expand user home directory (~) if present
    fileLocation = os.path.expanduser(fileLocation.strip())
    # Convert to absolute path
    fileLocation = os.path.abspath(fileLocation)
    # Ensure the directory exists
    os.makedirs(fileLocation, exist_ok=True)
else:
    # Use current directory if no location specified
    fileLocation = os.getcwd()

if fileName.lower().endswith(".csv"):
    fileName = fileName[:-4]

log = ACT.Parser(mode='logging', interface='can0',
                 loopback=False, output_type='csv', output_name=fileName,
                 parse_type="smart_nox", output_location=fileLocation)
log.configure_smart_nox_output()

print("Logging CAN Data (crtl+C to exit)...")
log.beginLogging()
