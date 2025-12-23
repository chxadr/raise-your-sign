# Raise Your Sign

An interactive quiz program that allows users to respond to questions by raising signs.

## For developers

### Installing the project

To get started, first clone the GitHub repository to your local machine:

```sh
git clone https://github.com/chxadr/raise-your-sign.git
cd raise-your-sign
```
Next, you need to install the project setup.

- **On UNIX-like systems:**

  Simply run the following command in your terminal:

  ```sh
  make install
  ```

  This will install the necessary dependencies. Make sure you have **Python 3.13**
  installed before running this command.

- **On Windows:**

  You can use the [Python Install Manager](https://www.python.org/downloads/windows/)
  to install Python 3.13 and manage your Python environments. It’s a really handy tool!

  Run the provided script from **Command Prompt** (not PowerShell, as it may not work):

  ```cmd
  scripts\envinstall.cmd
  ```

  This will install Pyhton 3.13 (if you have the Python Install Manager installed)
  and provide the necessary dependencies.

### Cleaning files

Sometimes when you add or remove features in the project, it's important to clear Python's cache. This can help prevent strange bugs.

- **On UNIX-like systems:**

  You can clean up the cache and other generated files by running:

  ```sh
  make clean
  ```

- **On Windows:**

  Use the provided script to clean up:

  ```cmd
  scripts\clean.cmd
  ```

### Test your code

> [!IMPORTANT]  
> Add explanations for code testing.
