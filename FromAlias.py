import os
import platform
dir_location = __file__.replace(os.path.basename(__file__), "")

with open(os.path.join(dir_location, "environment.path"), "r") as f:
    env_path = f.read()

def main():
    main_file = os.path.join(dir_location, "main.py")
    if platform.system() == "Windows":
        os.system(f"{env_path}\\python.exe {main_file}")
    else:
        os.system(f"sudo {env_path}/bin/python {main_file}")
