
import subprocess
import sys
import os

def run_debug():
    print("Running simulator in debug mode...")
    env = os.environ.copy()
    # Force output to be unbuffered
    env["PYTHONUNBUFFERED"] = "1"
    
    process = subprocess.Popen(
        [sys.executable, "run_gui.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=os.getcwd()
    )
    
    try:
        stdout, stderr = process.communicate(timeout=15)
        print("STDOUT:")
        print(stdout)
        print("STDERR:")
        print(stderr)
        print(f"Exit Code: {process.returncode}")
    except subprocess.TimeoutExpired:
        print("Process timed out (still running or stuck)")
        process.kill()
        stdout, stderr = process.communicate()
        print("STDOUT (captured before timeout):")
        print(stdout)
        print("STDERR (captured before timeout):")
        print(stderr)

if __name__ == "__main__":
    run_debug()
