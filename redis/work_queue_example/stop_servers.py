import subprocess
import os


def stop_servers():
    # Kill any Python processes running the web or model servers
    try:
        subprocess.run(["pkill", "-f", "run_web_server.py"], check=True)
        print("Web server stopped")
    except subprocess.CalledProcessError:
        print("No web server process found")

    try:
        subprocess.run(["pkill", "-f", "run_model_server.py"], check=True)
        print("Model server stopped")
    except subprocess.CalledProcessError:
        print("No model server process found")


if __name__ == "__main__":
    stop_servers()
