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

requirements = [
    "mouse==0.7.1", "keyboard==0.13.5", "PyQt5==5.15.9", "PyQt5.sip==12.11.1", "lxml==4.9.2",
    "gitPython==3.1.31", "fast_autocomplete==0.9.0", "fast-autocomplete[levenshtein]==0.9.0"
]

python_version = "3.11.2"
project_name = "labelapp"


def get_conda_path():
    global cmd, output, error
    send("conda info --base")
    while (out := get_stdout()) == []:
        time.sleep(.3)
    return out[0].replace("\n", "")

def list_contains(string: str, lines: list) -> bool:
    for line in lines:
        if string in line:
            return True
    return False

def reset_stream(stream: io.TextIOWrapper):
    stream.seek(0)
    stream.truncate(0)
    stream.write('')

def get_lines(file: io.TextIOWrapper, prefix: str) -> list[str]:
    global log
    file.seek(0)
    lines = file.readlines()
    reset_stream(file)

    index = 0
    while index < len(lines):
        if lines[index] == '' or lines[index] == '\n':
            lines.pop(index)
            continue
        index += 1

    if lines != []:
        log.write(prefix+''.join(lines))
        log.flush()
    return lines

def get_stdout() -> list[str]:
    global output
    return get_lines(output, "[STDOUT]")

def get_stderr() -> list[str]:
    global error
    return get_lines(error, "[STDERR]")

def send(data: str):
    global cmd
    cmd.stdin.write((data + '\n').encode('utf-8'))
    cmd.stdin.flush()

def reset():
    global cmd, output, error
    reset_stream(output)
    reset_stream(error)
    cmd.stdin.write(('exit\n').encode('utf-8'))
    cmd.stdin.flush()
    cmd = subprocess.Popen(["bash"], stdout=output, stderr=error, stdin=subprocess.PIPE)

def close_cmd():
    global cmd, output, error, log
    cmd.terminate()
    output.close()
    error.close()
    log.close()

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

def ask_for_branch(at: str) -> str:
    repo = git.Repo.clone_from("https://github.com/Felipe-Hideki/labelling-app.git", at)
    branches = repo.remote("origin").fetch()

    print("Available branches:")
    for i, branch in enumerate(branches):
        print(f"{i}: {branch.name.split('/')[-1]}")
    
    branch = input("Which branch do you want to install? (default: main): ")
    while branch not in [str(i) for i in range(len(branches))] and branch != "":
        os.system("clear")
        branch = input("Invalid branch. Please enter a valid branch: ")
        branch = input("Which branch do you want to install? (default: main): ")

    if branch == "":
        return "main"
    
    try:
        branch = branches[int(branch)].name.split('/')[-1]
    finally:
        return branch

def change_branch(branch: str, at: str):
    repo = git.Repo(at)
    repo.git.checkout(branch)

def onMain():
    # Check if conda is installed
    process = subprocess.run(["conda", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = process.stderr.decode("utf-8")

    if "conda: command not found" in err:
        print("Conda not found. Please install conda to continue.\n")
        input()
        exit()

    # Get path to install
    path = input(f"Where do you want to install the app? (default: ~/{project_name}): ")
    while(not os.path.exists(path) and path != ""):
        print("Invalid path. Please enter a valid path.")
        path = input(f"Where do you want to install the app? (default: ~/{project_name}): ")

    if path == "":
        path = os.path.join(os.path.expanduser("~"), project_name)

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
            change_branch(ask_for_branch(path), path)
    else:
        change_branch(ask_for_branch(path), path)
    print("Installing environment...\n")

    # Create output file stream
    open("output.txt", 'w').close()
    open("error.txt", 'w').close()
    global env_path, output, error, log, cmd

    output = open("output.txt", 'r+')
    error = open("error.txt", 'r+')
    log = open("log.txt", 'w')

    out = []

    cmd = subprocess.Popen(["bash"], stdout=output, stderr=error, stdin=subprocess.PIPE)

    send(f"conda create -n {project_name} -c conda-forge python={python_version}")
    # Wait for process to finish
    while cmd.poll() is None:
        err = get_stderr()
        out = get_stdout()

        if err != []:
            print("".join(err))
            if list_contains("CondaSystemExit", err):
                reset()
                break

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
            elif list_contains("Proceed ([y]/n)?", out):
                 send(input())
            elif list_contains(f"$ conda activate {project_name}", out):
                break
        time.sleep(.3)

    conda_path = get_conda_path()
    env_path = os.path.join(conda_path, f"envs/{project_name}")
    pip_path = os.path.join(env_path, "bin/pip3")

    send(f"source {conda_path}/etc/profile.d/conda.sh && conda activate {project_name}")
    send("echo done")
    while (out := get_stdout()) == []:
        if list_contains("done", get_stderr()):
            break
        time.sleep(.3)

    send("which pip")
    time.sleep(5)

    print("\nInstalling dependencies... \n")
    # Install dependencies

    with open(os.path.join(path, 'requirements.txt'), 'w') as f:
        [f.write(line+'\n') for line in requirements]

    with open(os.path.join(path, 'environment.path'), 'w') as f:
        f.write(env_path)
    #send("source ~/anaconda3/etc/profile.d/conda.sh")
    send(f"{pip_path} install gitPython && {pip_path} install -e {path} \
        && {pip_path} install -r {os.path.join(path, 'requirements.txt')} && conda deactivate \
        && echo 'Installation complete. You can now run the app by typing 'sudo labelapp' in your terminal with the conda enviroment active.'")

    while cmd.poll() is None:
        out = get_stdout()
        err = get_stderr()
        if err != []:
            if not list_contains("notice", err):
                print("Installation failed. Please check the log file for more information.")
                close_cmd()
                exit()
        if out != []:
            [print(line, end="") for line in out]
            if list_contains("Installation complete", out):
                break
        time.sleep(.3)

    close_cmd()

def Setup():
    setuptools.setup(
        name="labelling_app",
        version="0.0.1",
        author="Japa",
        python_requires=">=3.11",
        packages=setuptools.find_packages(),
        entry_points={
            "console_scripts": [
                "labelapp=FromAlias:main",
            ]
        },
        # install_requires=[
        #     "mouse==0.7.1", "keyboard==0.13.5", "PyQt5==5.15.9", "PyQt5.sip==12.11.1", "lxml==4.9.2",
        #     "gitPython==3.1.31", "fast_autocomplete==0.9.0", "fast-autocomplete[levenshtein]==0.9.0"
        # ]
    )
if __name__ == "__main__":
    if sys.argv and len(sys.argv) > 0 and sys.argv[1] == "install":
        onMain()
        input("Press any key to exit...")
        exit()
    Setup()