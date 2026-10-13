# Raise Your Sign

An interactive quiz program where users can vote by raising signs. 

## Prerequisites

Before setting up the project, ensure you have the following installed:

* **Python 3.13**
* **Make** (for UNIX-like systems)
* **[Python Install Manager](https://www.python.org/downloads/windows/)** (recommended for Windows)

## Installation

### 1. Repository
Clone the repository and navigate into the project directory:

```sh
git clone https://github.com/chxadr/raise-your-sign.git
cd raise-your-sign
```

### 2. Dependencies
Run the environment setup script:

* **UNIX-like Systems:**
  ```sh
  make install
  ```
* **Windows:**
  Open **Command Prompt** (do not use PowerShell) and execute:
  ```cmd
  scripts\envinstall.cmd
  ```

## Testing the Application

Once the installation is complete, verify your setup by running:

```sh
cd tests
python test.py
```

## Building the Executable

You can compile the application into a standalone executable file.

### On UNIX-like Systems
1. Build the binary:
   ```sh
   make build
   ```
2. Run the newly compiled executable:
   ```sh
   make run
   ```
The compiled files are located inside the `main/dist/` directory.

### On Windows
1. Open **Command Prompt** and build the binary:
   ```cmd
   scripts\compilexe.cmd
   ```
2. Navigate to the `main/dist/` directory to locate and launch your `quiz.exe` file.

## Cleaning

If you make modifications to the codebase, it is recommended to clear Python's cache and build artifacts to prevent unexpected behavior.

* **UNIX-like Systems:**
  ```sh
  make clean
  ```
* **Windows:**
  ```cmd
  scripts\clean.cmd
  ```
