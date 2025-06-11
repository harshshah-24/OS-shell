import sys
import shutil
import subprocess
import shlex
import os
import readline
import contextlib

tab_count = 0
last_text = ""

def find_longest_common_prefix(strs):
    if not strs:
        return ""
    shortest = min(strs, key=len)
    for i, char in enumerate(shortest):
        for other in strs:
            if other[i] != char:
                return shortest[:i]
    return shortest

def completer(text, state):
    global tab_count, last_text
    if text == last_text:
        tab_count += 1
    else:
        tab_count = 0
    last_text = text

    builtins = ["echo", "exit", "type", "pwd", "cd", "ls", "calc", "crfile", "dlfile", "cpyfile"]
    completions = []

    for cmd in builtins:
        if cmd.startswith(text):
            completions.append(cmd)

    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not os.path.isdir(directory):
            continue
        try:
            for file in os.listdir(directory):
                if file.startswith(text):
                    full_path = os.path.join(directory, file)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        if file not in completions:
                            completions.append(file)
        except Exception:
            continue

    completions.sort()
    if not completions:
        return None
    elif len(completions) == 1:
        return completions[0] + " " if state == 0 else None
    else:
        lcp = find_longest_common_prefix(completions)
        if len(lcp) > len(text):
            return lcp if state == 0 else None
        elif tab_count == 1:
            print("\n" + "  ".join(completions))
            sys.stdout.write("$ " + text)
            sys.stdout.flush()
            return None
        else:
            sys.stdout.write("\a")
            sys.stdout.flush()
            return None

def setup_readline():
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

def echo(command_parts):
    print(" ".join(command_parts[1:]))

def pwd(command_parts):
    print(os.getcwd())

def cd(command_parts):
    if len(command_parts) == 1:
        print("cd: missing argument", file=sys.stderr)
        return
    elif len(command_parts) == 2:
        target = os.path.expanduser(command_parts[1])
    else:
        print("cd: too many arguments", file=sys.stderr)
        return

    try:
        os.chdir(target)
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target}", file=sys.stderr)

def ls(command_parts):
    try:
        entries = os.listdir(os.getcwd())
        entries.sort()
        for entry in entries:
            print(entry)
    except Exception as e:
        print(f"ls: {e}", file=sys.stderr)

def calc(command_parts):
    if len(command_parts) != 4:
        print("calc: invalid syntax. Usage: calc operand1 operation operand2", file=sys.stderr)
        return

    _, operand1, operator, operand2 = command_parts

    try:
        op1 = float(operand1)
        op2 = float(operand2)
    except ValueError:
        print("calc: operands must be numbers", file=sys.stderr)
        return

    if operator == '+':
        result = op1 + op2
    elif operator == '-':
        result = op1 - op2
    elif operator == '*':
        result = op1 * op2
    elif operator == '/':
        if op2 == 0:
            print("calc: division by zero", file=sys.stderr)
            return
        result = op1 / op2
    elif operator == '%':
        if op2 == 0:
            print("calc: modulo by zero", file=sys.stderr)
            return
        result = op1 % op2
    else:
        print(f"calc: unsupported operator '{operator}'", file=sys.stderr)
        return

    if operand1.isdigit() and operand2.isdigit() and operator != '/':
        result = int(result)
    print(result)

def crfile(command_parts):
    
    if len(command_parts) != 2:
        print("crfile: invalid syntax. Usage: crfile filename", file=sys.stderr)
        return

    filename = command_parts[1]
    try:
        with open(filename, "w") as f:
            pass
    except Exception as e:
        print(f"crfile: error creating file '{filename}': {e}", file=sys.stderr)

def dlfile(command_parts):

    if len(command_parts) != 2:
        print("dlfile: invalid syntax. Usage: dlfile filename", file=sys.stderr)
        return

    filename = command_parts[1]
    try:
        os.remove(filename)
    except Exception as e:
        print(f"dlfile: error deleting file '{filename}': {e}", file=sys.stderr)

def cpyfile(command_parts):

    if len(command_parts) != 3:
        print("cpyfile: invalid syntax. Usage: cpyfile source_file destination_file", file=sys.stderr)
        return

    source_file = command_parts[1]
    destination_file = command_parts[2]
    try:
        shutil.copyfile(source_file, destination_file)
    except Exception as e:
        print(f"cpyfile: error copying from '{source_file}' to '{destination_file}': {e}", file=sys.stderr)

def type_cmd(command_parts):
    if len(command_parts) < 2:
        print("type: missing argument", file=sys.stderr)
        return
    cmd = command_parts[1]
    builtins = ["echo", "exit", "type", "pwd", "cd", "ls", "calc", "crfile", "dlfile", "cpyfile"]
    if cmd in builtins:
        print(f"{cmd} is a shell builtin")
    elif path := shutil.which(cmd):
        print(f"{cmd} is {path}")
    else:
        print(f"{cmd}: not found")

built_ins = {
    "echo": echo,
    "pwd": pwd,
    "cd": cd,
    "ls": ls,
    "calc": calc,
    "crfile": crfile,
    "dlfile": dlfile,
    "cpyfile": cpyfile,
    "type": type_cmd,
}

def main():
    setup_readline()
    while True:
        sys.stdout.write(os.getcwd() + " $ ")
        sys.stdout.flush()
        try:
            input_string = input()
        except EOFError:
            break

        try:
            input_parts = shlex.split(input_string)
        except ValueError:
            print("Error: Unmatched quote", file=sys.stderr)
            continue

        if not input_parts:
            continue

        redirect_type = None
        redirect_file = None
        command_parts = input_parts
        if len(input_parts) >= 2:
            if input_parts[-2] in [">", "1>"]:
                redirect_type = ">"
                redirect_file = input_parts[-1]
                command_parts = input_parts[:-2]
            elif input_parts[-2] in [">>", "1>>"]:
                redirect_type = ">>"
                redirect_file = input_parts[-1]
                command_parts = input_parts[:-2]
            elif input_parts[-2] in ["2>", "2>>"]:
                if input_parts[-2] == "2>>":
                    redirect_type = "2>>"
                else:
                    redirect_type = "2>"
                redirect_file = input_parts[-1]
                command_parts = input_parts[:-2]

        if not command_parts:
            continue

        command = command_parts[0]

        if command == "exit":
            if len(command_parts) == 2 and command_parts[1] == "0":
                break
            else:
                print("Invalid exit command", file=sys.stderr)
            continue

        if command in built_ins:
            if redirect_type == ">":
                try:
                    with open(redirect_file, "w") as f:
                        with contextlib.redirect_stdout(f):
                            built_ins[command](command_parts)
                except (FileNotFoundError, PermissionError) as e:
                    print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
            elif redirect_type == ">>":
                try:
                    with open(redirect_file, "a") as f:
                        with contextlib.redirect_stdout(f):
                            built_ins[command](command_parts)
                except (FileNotFoundError, PermissionError) as e:
                    print(f"cannot open file {redirect_file} for appending: {e}", file=sys.stderr)
            elif redirect_type == "2>":
                try:
                    with open(redirect_file, "w") as f:
                        original_stderr = sys.stderr
                        sys.stderr = f
                        try:
                            built_ins[command](command_parts)
                        finally:
                            sys.stderr = original_stderr
                except (FileNotFoundError, PermissionError) as e:
                    print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
            elif redirect_type == "2>>":
                try:
                    with open(redirect_file, "a") as f:
                        original_stderr = sys.stderr
                        sys.stderr = f
                        try:
                            built_ins[command](command_parts)
                        finally:
                            sys.stderr = original_stderr
                except (FileNotFoundError, PermissionError) as e:
                    print(f"cannot open file {redirect_file} for appending stderr: {e}", file=sys.stderr)
            else:
                built_ins[command](command_parts)
        else:
            full_path = shutil.which(command)
            if full_path:
                args = [command] + command_parts[1:]
                if redirect_type == ">":
                    try:
                        with open(redirect_file, "w") as f:
                            subprocess.run(args, executable=full_path, stdout=f, stderr=sys.stderr)
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
                elif redirect_type == ">>":
                    try:
                        with open(redirect_file, "a") as f:
                            subprocess.run(args, executable=full_path, stdout=f, stderr=sys.stderr)
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot open file {redirect_file} for appending: {e}", file=sys.stderr)
                elif redirect_type == "2>":
                    try:
                        with open(redirect_file, "w") as f:
                            subprocess.run(args, executable=full_path, stderr=f, stdout=sys.stdout)
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
                elif redirect_type == "2>>":
                    try:
                        with open(redirect_file, "a") as f:
                            subprocess.run(args, executable=full_path, stderr=f, stdout=sys.stdout)
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot open file {redirect_file} for appending stderr: {e}", file=sys.stderr)
                else:
                    subprocess.run(args, executable=full_path)
            else:
                error_msg = f"{command}: not found"
                if redirect_type == ">":
                    try:
                        with open(redirect_file, "w") as f:
                            f.write(error_msg + "\n")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
                elif redirect_type == ">>":
                    try:
                        with open(redirect_file, "a") as f:
                            f.write(error_msg + "\n")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot open file {redirect_file} for appending: {e}", file=sys.stderr)
                elif redirect_type == "2>":
                    try:
                        with open(redirect_file, "w") as f:
                            f.write(error_msg + "\n")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot create file {redirect_file}: {e}", file=sys.stderr)
                elif redirect_type == "2>>":
                    try:
                        with open(redirect_file, "a") as f:
                            f.write(error_msg + "\n")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"cannot open file {redirect_file} for appending stderr: {e}", file=sys.stderr)
                else:
                    print(error_msg, file=sys.stderr)

if __name__ == "__main__":
    main()