import os
import time
import subprocess

# Helper to run a script for a set duration (in seconds)
def run_script_for(script_path, duration=None):
    proc = subprocess.Popen(["python", script_path])
    if duration is not None:
        try:
            time.sleep(duration)
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
    else:
        proc.wait()

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    log_one = os.path.join(folder, "logOne.py")
    log_two = os.path.join(folder, "logTwo.py")
    log_three = os.path.join(folder, "logThree.py")

    # Run logOne for 30 minutes (1800 seconds)
    run_script_for(log_one, duration=1800)
    # Run logTwo for 30 minutes (1800 seconds)
    run_script_for(log_two, duration=1800)
    # Run logThree forever (until this script is stopped)
    run_script_for(log_three, duration=None)

