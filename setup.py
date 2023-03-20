import sys
import shutil
import setuptools
import subprocess
import os
import git
import time
import io
import select
from threading import Thread
from queue import Queue, Empty

def list_contains(string: str, lines: list) -> bool:
    for line in lines:
        if string in line:
            return True
    return False

def get_lines(file: io.TextIOWrapper) -> list[str]:
    file.seek(0)
    lines = file.readlines()
    file.seek(0)
    file.truncate(0)
    file.write('')
    return lines

def get_stdout() -> list[str]:
    global output
    return get_lines(output)

def get_stderr() -> list[str]:
    global error
    return get_lines(error)

def send(data: str):
    global cmd
    cmd.stdin.write((data + '\n').encode('utf-8'))
    cmd.stdin.flush()

def reset():
    global cmd
    cmd.stdin.write(('exit\n').encode('utf-8'))
    cmd.stdin.flush()
    cmd = subprocess.Popen(["bash"], stdout=output, stderr=error, stdin=subprocess.PIPE)

def write_to_process(process: subprocess.Popen, data: str):
    while data:
         # check if the stdin stream is ready for writing
        rlist, wlist, xlist = select.select([], [process.stdin], [], 0)
        if wlist:
            # write the data to stdin
            n = wlist[0].write(data)
            data = data[n:]
            print("wrote %d bytes" % n)
    print("done writing")

def onMain():
    # Check if conda is installed
    process = subprocess.run(["conda", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = process.stderr.decode("utf-8")

    if "conda: command not found" in err:
        print("Conda not found. Please install conda to continue.\n")
        input()
        exit()

    # Get path to install
    path = input("Where do you want to install the app? (default: ~/labelling_app): ")
    while(not os.path.exists(path) and path != ""):
        path = input("Invalid path. Please enter a valid path: ")
        path = input("Where do you want to install the app? (default: ~/labelling_app): ")

    if path == "":
        path = os.path.join(os.path.expanduser("~"), "labelling_app")

    if os.path.exists(path):
        ans = input("Folder already exists. Do you want to overwrite? (y/n): ")
        while ans not in ["y", "n"]:
            ans = input("Folder already exists. Do you want to overwrite? (y/n): ")
            if ans in ["y", "n"]:
                break
            os.system("clear")
            print("Invalid input. Please enter 'y' or 'n'.")
  
        if ans == "y":
            shutil.rmtree(path)
            # Clone repo
            print(f"Starting Download at path {path}...")
            git.Repo.clone_from("https://github.com/Felipe-Hideki/labelling-app.git", path, branch="main")
            print("Download Complete!")
    print("Installing environment...\n")

    # Create output file stream
    open("output.txt", 'w').close()
    open("error.txt", 'w').close()
    global output
    global error

    output = open("output.txt", 'r+')
    error = open("error.txt", 'r+')

    log = open("log.txt", 'w')

    global cmd

    out = []

    cmd = subprocess.Popen(["bash"], stdout=output, stderr=error, stdin=subprocess.PIPE)

    send("conda create -n labelling_app -c conda-forge python=3.11")
    # Wait for process to finish
    while cmd.poll() is None:
        err = get_stderr()
        out = get_stdout()

        if err != []:
            print("".join(err))

        # Check if output has changed
        if out != []:
            # print output
            [print(line, end="") for line in out]
            log.write(''.join(out)+"\n")
            # Check if conda env already exists
            if list_contains("conda environment already exists", out):
                # write_to_process(process, (input() + '\n').encode('utf-8'))
                inp = input()
                send(inp)
                if inp == 'n':
                    reset()
            elif list_contains("Proceed ([y]/n)?", out):
                 send(input())
            elif list_contains("$ conda activate labelling_app", out):
                break
        time.sleep(.3)

    print("\nInstalling dependencies... \n")
    # Install dependencies
    send("source ~/anaconda3/etc/profile.d/conda.sh")
    send(f"conda activate labelling_app && pip install gitPython && pip install -e {path} \
        && pip freeze && conda deactivate && echo exit")

    while cmd.poll() is None:
        out = get_stdout()
        err = get_stderr()
        if err != []:
            print("".join(err))
            exit()
        if out != []:
            [print(line, end="") for line in out]
            log.write(''.join(out)+"\n")
            if list_contains("exit", out):
                break
        time.sleep(.3)

    cmd.terminate()
    output.close()

def Setup():
    setuptools.setup(
        name="labelling_app",
        version="0.0.1",
        author="Japa",
        python_requires=">=3.11",
        packages=setuptools.find_packages(),
        entry_points={
            "console_scripts": [
                "labelapp=main.main:main",
            ]
        },
        install_requires=[
            "mouse", "keyboard", "PyQt5", "PyQt5.sip", "gitPython", "fast_autocomplete"
        ]
    )
if __name__ == "__main__":
    if sys.argv and len(sys.argv) > 0 and sys.argv[1] == "install":
        onMain()
        input("Press any key to exit...")
        exit()
    Setup()