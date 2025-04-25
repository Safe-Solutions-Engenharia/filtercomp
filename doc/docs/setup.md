# Setup Guide

---

## Prerequisites

Ensure your system has the following installed:

* [Python 3.10+](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/)
* [Git](https://git-scm.com/)
* [DWSIM](https://dwsim.org/)
---

## Cloning the Project

Clone the repository to your local machine:
```bash 
git clone https://github.com/Safe-Solutions-Engenharia/filtercomp.git
cd filtercomp
```

---

## Creating a Virtual Enviroment


Create and activate a virtual environment:

=== "Windows"

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

=== "Linux/macOS"

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

---

## Installing Dependencies

Install dependencies listed in requirements.txt:

```py
pip install -r requirements.txt
```