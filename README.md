# PyShell

## Overview

PyShell is a lightweight command-line shell implemented in Python. It provides basic shell functionalities including built-in commands, tab-based auto-completion, I/O redirection, and execution of external programs.

## Features

* **Built-in Commands**: `echo`, `pwd`, `cd`, `ls`, `calc`, `crfile`, `dlfile`, `cpyfile`, `type`, and `exit`.
* **Auto-Completion**: Tab-based completion for built-in commands and executables in the system `PATH`.
* **I/O Redirection**: Supports standard output and error redirection (`>`, `>>`, `2>`, `2>>`).
* **External Commands**: Executes any executable available in the system `PATH`.
* **Error Handling**: Graceful handling of invalid inputs and file-related errors.

## Requirements

* Python 3.6 or higher
* Unix-like operating system (Linux, macOS) or Windows with appropriate ANSI support

## Installation

1. Clone the repository or download the `main1.py` file.
2. Ensure the file has executable permissions:

   ```bash
   chmod +x main1.py
   ```
3. Run the shell:

   ```bash
   ./main1.py
   ```

## Usage

When launched, PyShell displays the current working directory as a prompt. Enter commands as you would in a standard shell.

```bash
/home/user $ ls
Documents  Downloads  main1.py
/home/user $ pwd
/home/user
/home/user $ calc 10 + 5
15
/home/user $ crfile example.txt
/home/user $ ls
Documents  Downloads  example.txt  main1.py
/home/user $ exit 0
```

## Built-in Commands

| Command   | Description                                                                               |
| --------- | ----------------------------------------------------------------------------------------- |
| `echo`    | Prints its arguments to standard output.                                                  |
| `pwd`     | Displays the current working directory.                                                   |
| `cd`      | Changes the current directory. Usage: `cd <directory>`.                                   |
| `ls`      | Lists files and directories in the current directory.                                     |
| `calc`    | Performs basic arithmetic. Usage: `calc <num1> <op> <num2>` (`+`, `-`, `*`, `/`, `%`).    |
| `crfile`  | Creates an empty file. Usage: `crfile <filename>`.                                        |
| `dlfile`  | Deletes a file. Usage: `dlfile <filename>`.                                               |
| `cpyfile` | Copies a file. Usage: `cpyfile <source> <destination>`.                                   |
| `type`    | Identifies if a command is a built-in or an external executable. Usage: `type <command>`. |
| `exit`    | Exits the shell. Usage: `exit 0` for a clean exit.                                        |

## Auto-Completion

* Press `Tab` to complete built-in commands or program names in `PATH`.
* If multiple matches exist, a second `Tab` lists all possible completions.

## I/O Redirection

* Redirect standard output: `>` (overwrite), `>>` (append).
* Redirect standard error: `2>` (overwrite), `2>>` (append).
* Example:

  ```bash
  ls > files.txt      # Save listing to files.txt
  calc 1 / 0 2> error.log # Log division error to error.log
  ```

## External Commands

Any executable available in the system `PATH` can be run directly. Arguments and redirection work as expected.

```bash
/home/user $ grep "pattern" file.txt > results.txt
```

## Error Handling

PyShell prints descriptive error messages for:

* Invalid commands
* Missing or extra arguments
* File not found or permission issues
* Division or modulo by zero in `calc`

## Contributing

Contributions, bug reports, and feature requests are welcome. Please fork the repository and submit a pull request.

## License

This project is released under the MIT License. See the `LICENSE` file for details.
