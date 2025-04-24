<h1 align="center">
  <b>FilterComp</b>
  <br>
</h1>

<div align="center">

![Static Badge](https://img.shields.io/badge/made%20with-python-blue?style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/Safe-Solutions-Engenharia/filtercomp)
![GitHub License](https://img.shields.io/github/license/Safe-Solutions-Engenharia/filtercomp)

</div>

A tool for filtering scenarios and performing flash calculations with **DWSIM** integration. It allows users to analyze scenarios based on predefined criteria, providing a structured and efficient way to flash multiple components.

## Instalation

Clone the repository:
```sh
git clone https://github.com/Safe-Solutions-Engenharia/filtercomp.git
cd src
```

Install dependencies:
```sh
pip install -r requirements.txt
```

Run the application:
```sh
python main.py
```

## Usage

1. Download and install the latest version of DWSIM.
2. Generate an `.xlsx` file similar to [composicao_teste.xlsx](/tests/composicao_teste.xlsx), ensuring it contains the necessary data for analysis.
3. Open and modify [global_variables.py](/src/config/global_variables.py) as needed to match the desired output.
4. Execute the main script.
5. Retrieve the output folder, which should resemble [Overall](/tests/Overall/).

## Features

- Automatic flashing of multiple currents with various compounds.
- Filtering currents using specific, unique methods.
- Clean and structured data output from the analysis.

## Acknowledgments

This project utilizes **DWSIM**, an open-source chemical process simulator, to enhance certain calculations and simulations.  
We acknowledge the DWSIM developers and contributors for their invaluable work.

- 🔗 [DWSIM Official Website](https://dwsim.org/)
- 🔗 [DWSIM GitHub Repository](https://github.com/DanWBR/dwsim)

## Learn More

For additional information and resources, check out the following:

- [FilterComp Docs](https://safe-solutions-engenharia.github.io/filtercomp/).

## License

[GNU General Public License v3.0](./LICENSE) © FilterComp
