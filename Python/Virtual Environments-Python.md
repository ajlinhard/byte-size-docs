# Python Virtual Environments (Venv) vs. Anaconda Environements (Conda)
Virutal Environments are how you handle different python package dependency builds for your projects. They can help you manage different versioning required for projects, services, or dev/test comparisons.
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
