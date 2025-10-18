import subprocess
import time
import os


def start_servers():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Start the model server in the background
    print("Starting model server...")
    model_process = subprocess.Popen(
        ["python", os.path.join(current_dir, "run_model_server.py")]
    )

    # Wait a moment for the model server to start
    time.sleep(2)

    # Start the web server in the background
    print("Starting web server...")
    web_process = subprocess.Popen(
        ["python", os.path.join(current_dir, "run_web_server.py")]
    )

    # Wait a moment for the web server to start
    time.sleep(2)

    print("Servers started successfully!")
    print("Model server PID:", model_process.pid)
    print("Web server PID:", web_process.pid)

    return model_process, web_process


if __name__ == "__main__":
    start_servers()
