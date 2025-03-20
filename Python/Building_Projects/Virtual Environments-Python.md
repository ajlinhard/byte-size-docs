# Python Virtual Environments (Venv, Anaconda, Poetry, Virtualenv, Pipenv)
Virutal Environments are how you handle different python package dependency builds for your projects. They can help you manage different versioning required for projects, services, or dev/test comparisons.

## FIRST! How do python scripts execute?
When you execute or import a python module/script, the code runs from the path it is at. However, the python execution runs from where the environment/interpreter (aka python.exe) lives. All libraries must be installed in the under the location of the interpreters location, or the sys.path of your project must be added at runtime (in the script).

Option 2: Manual Execution
You can also have the path added to execution by calling the module from the project folder with the following command:
```bash
cd /Full/Project/Path/
python -m package_folder.subfolder.script
```
Option 3: Install Project Quickly to Environment
You can run this command from your project directory to quickly install the project
** Note: If you make changed you need to re-install **
```bash
# ACTIVATE Python Environment
pip install -e
# or
pip install -e /path/to/your/project
```

Option 4: Adhoc scripts and Notebooks
If you need to test a script quickly adhocly or if using notebooks, which cannot be run conviently be run on the command line. Then use the following techniques:
```python
import os
import sys

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(script_dir, '..'))  # Adjust as needed for your folder structure
sys.path.insert(0, project_root)

# Now you can import modules from your project
import your_project_module
```
For Notebooks:
Since, notebooks execute under __main__ and __file___ is not defined.
```python
import os
import sys

# Get notebook directory
notebook_dir = os.getcwd()

# Navigate to project root (adjust '../' as needed based on notebook location)
project_root = os.path.abspath(os.path.join(notebook_dir, '..'))
sys.path.insert(0, project_root)

# Now you can import modules from your project
import your_project_module
```
### Debugging Import Errors
Import errors can be difficult to figure out and usually have to do with where you are executing the python scripts

- [Helpful Import Error Debug Example](https://www.youtube.com/watch?v=pm1IK0fBuhw)

## Good Documentation
- [Basics of Each Virtual Env](https://www.pythoncheatsheet.org/cheatsheet/virtual-environments)

# Venv:
    - create a Venv directly in your project folder:
        1. python -m venv api_env
        2. api_env\Scripts\activate
        3. Install Packages
            a. pip install flask
            b. pip install flask-cors
            c. pip install flask-
    - Pros:
        - Quicker setup since all the base anaconda packages are not installed.
    - Cons:
        - The environment only exists within the folder the Venv is made

# Anaconda:
    - Anaconda environments persist across projects and are accessible throughout system installed on.
    - Separate terminal for conda.
