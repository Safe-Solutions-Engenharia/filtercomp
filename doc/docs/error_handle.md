# FAQ

## Configuration

???+ question "An error appeared during the installation of the 'requirements.txt' file"
    Try using one of the following specific Python versions in the virtual environment: **3.10.1**,  **3.11.0**, **3.13.0**. 
    If the error persists, open an issue in the project's repository.

???+ question "I installed the correct version of DWSIM, but the code can't seem to find it"
    If it's a fresh install, try opening it once, running and saving a simple project, then try the code again. 
    If not, check if the code is being run by the user whose account contains the DWSIM folder in the _AppData_ directory.

## Results

???+ question "Why are my results different from the DWSIM GUI?"
    Discrepancies often occur because the automation interface may revert custom Property Package parameters to their defaults, leading to different calculation results.

    **Solution:**
    To ensure consistency, initialize the simulation using a pre-configured template:

    1. Create a DWSIM simulation containing **one** material stream and all required components.
    2. Save it as a `.dwxmz` file.
    3. Update the `TEMPLATE` variable in `global_variables.py` with the path to this new file.