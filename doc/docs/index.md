<h1 align="center">
  <b>FilterComp</b>
  <br>
</h1>

---

Welcome to **FilterComp**, a tool developed by **Safe Solutions Engenharia** for filtering, processing, and comparing datasets using the flash calculation logic from **DWSIM**.

This tool was designed to streamline data analysis pipelines, enabling users to filter large datasets based on dynamic criteria, apply statistical and logical comparisons.

---

## Project Structure

Below is the core structure of the project, highlighting the most important components you'll interact with. The `src/` directory contains all the logic and entry points for running and testing the tool, while `utils/` groups the main modules responsible for file operations, formatting, filtering, and logging.

```text
filtercomp/
│
├── src/
│   ├── utils/
│   │   ├── file_saver.py        # Handles data saving
│   │   ├── format_files.py      # Handles data formatting
│   │   ├── logger.py            # Logging setup and utilities
│   │   ├── operation_filter.py  # Filtering logic after flashing operations
│   │   └── operations.py        # Defines flashing operations
│   │
│   ├── tests/                   # Unit tests for core functionality
│   └── main.py                  # Main file
│
└── requirements.txt             # Project dependencies
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository

2. Create a new feature branch

3. Make your changes and commit

4. Open a pull request for review