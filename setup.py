import sys
import shutil
import setuptools
import subprocess
import os
import platform
import time
import io
import select
import stat

try:
    import git
except ImportError:
    print("GitPython not found. trying to install...")
    os.system("pip install gitPython")
    import git

from threading import Thread
from queue import Queue, Empty

requirements = [
    "mouse==0.7.1", "keyboard==0.13.5", "PyQt5==5.15.9", "PyQt5.sip==12.11.1", "lxml==4.9.2",
    "gitPython==3.1.31", "fast_autocomplete==0.9.0", "fast-autocomplete[levenshtein]==0.9.0"
]

python_version = "3.11.2"
project_name = "labelapp"


if platform.system() == "Windows":
    def start_terminal(stdout, sterr, stdin) -> subprocess.Popen:
        return subprocess.Popen(["cmd"], stdout=stdout, stderr=sterr, stdin=stdin)
    def clear():
        os.system("cls")
    def get_pip_path(env_path: str) -> str:
        return os.path.join(env_path, "Scripts", "pip")
        
else:
    def start_terminal(stdout, sterr, stdin) -> subprocess.Popen:
        return subprocess.Popen(["bash"], stdout=stdout, stderr=sterr, stdin=stdin)
    def clear():
        os.system("clear")
    def get_pip_path(env_path: str) -> str:
        return os.path.join(env_path, "bin", "pip")

def get_conda_path() -> str:
    global cmd, output, error
    send("conda info --base > conda_path.txt && echo done")
    while not list_contains("done", (out := get_stdout())):
        time.sleep(.3)
    with open("conda_path.txt", 'r') as f:
        f.seek(0)
        path = f.readlines()[0].strip('\n')
    os.remove("conda_path.txt")
    return path

def list_contains(string: str, lines: list) -> bool:
    for line in lines:
        if string in line:
            return True
    return False

def reset_stream(stream: io.TextIOWrapper):
    stream.seek(0)
    stream.truncate(0)
    stream.write('')

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    print(f"Removed readonly from {path}")
    func(path)

def get_lines(file: io.TextIOWrapper, prefix: str) -> list[str]:
    global log
    file.seek(0)
    lines = file.readlines()
    reset_stream(file)

    index = 0
    while index < len(lines):
        if lines[index] == '' or lines[index] == '\n' or \
                lines[index].startswith(os.getcwd().split('\\')[0]) or \
                lines[index].startswith(f"({project_name})"):
            lines.pop(index)
            continue
        index += 1

    if lines != []:
        if lines[-1][-1] != '\n':
            lines[-1] += '\n'
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
    cmd.terminate()
    cmd = start_terminal(output, error, subprocess.PIPE)

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
        clear()
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
    while True:
        try:
            os.makedirs(path, exist_ok=True) if path != "" else None
            path = os.path.expanduser("~") if path == "" else path
            break
        except:
            print("Invalid path. Please enter a valid path.")
            path = input(f"Where do you want to install the app? (default: ~/{project_name}): ")

    if os.path.exists(path):
        print(path)
        ans = input("Folder already exists. Do you want to overwrite? (y/n): ")
        while ans not in ["y", "n"]:
            ans = input("Folder already exists. Do you want to overwrite? (y/n): ")
            if ans in ["y", "n"]:
                break
            clear()
            print("Invalid input. Please enter 'y' or 'n'.")
  
        if ans == "y":
            os.system(f"sudo rm -r {os.path.join(path, project_name)}")
            #shutil.rmtree(path, onerror=remove_readonly)
            print("Deleted folder Successfully.")
            os.mkdir(os.path.join(path, project_name))
            p_project = os.path.join(path, project_name)
            change_branch(ask_for_branch(p_project), p_project)
    else:
        os.makedirs(os.path.join(path, project_name), exist_ok=True)
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

    cmd = start_terminal(output, error, subprocess.PIPE)
    time.sleep(.2)
    get_stdout()

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
            #log.write(''.join(out)+"\n")
            # Check if conda env already exists
            if list_contains("conda environment already exists", out):
                # write_to_process(process, (input() + '\n').encode('utf-8'))
                send(input())
            elif list_contains("WARNING: A directory already exists at the target location", out):
                send(input())
            elif list_contains("Proceed ([y]/n)?", out):
                send(input())
            elif list_contains(f"$ conda activate {project_name}", out):
                break
        time.sleep(.3)

    conda_path = get_conda_path()
    env_path = os.path.join(conda_path,"envs", project_name)
    pip_path = get_pip_path(env_path)

    if platform.system() == "Windows":
        send(f"{conda_path}/Scripts/activate && conda activate {project_name}")
    else:
        send(f"source {conda_path}/etc/profile.d/conda.sh && conda activate {project_name}")
    send(f"conda install pip -y")
    send("echo done")
    while (out := get_stdout()) == []:
        if list_contains("done", get_stderr()):
            break
        time.sleep(.3)


    print("\nInstalling dependencies... \n")
    # Install dependencies

    with open(os.path.join(path, project_name, 'requirements.txt'), 'w') as f:
        [f.write(line+'\n') for line in requirements]

    with open(os.path.join(path, project_name, 'environment.path'), 'w') as f:
        f.write(env_path)
    #send("source ~/anaconda3/etc/profile.d/conda.sh")
    if platform.system() == "Windows":
        send(f"{pip_path} install gitPython && {pip_path} install -e {path} \
        && {pip_path} install -r {os.path.join(path, 'requirements.txt')} && conda deactivate \
        && echo 'Installation complete. You can now run the app by typing 'labelapp' in your terminal with the conda enviroment active.'")
    else:
        send(f"{pip_path} install gitPython && {pip_path} install -e {os.path.join(path, project_name)} \
            && {pip_path} install -r {os.path.join(path, 'requirements.txt')} && conda deactivate \
            && echo 'Installation complete. You can now run the app by typing 'sudo labelapp' in your terminal with the conda enviroment active.'")

    while cmd.poll() is None:
        out = get_stdout()
        err = get_stderr()
        if err != []:
            if not list_contains("notice", err) and not list_contains("WARNING", err):
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
        try:
            onMain()
        except Exception as e:
            if cmd:
                close_cmd()
        input("Press any key to exit...")
        exit()
    Setup()