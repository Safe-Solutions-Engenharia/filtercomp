import logging
import os

from enums.dwsim_packages import DWSIMPackages
from enums.format_type import FormatType
from enums.filter_operations import (OperationsFilter, PhaseType, CompoundBasis, 
                                     MolarFlowUnit, MassFlowUnit, PhaseActivity, PhaseInput)

current_dir = os.path.dirname(__file__) 

INPUT_FILE = os.path.abspath(os.path.join(current_dir, '../../files/test_files/composicao_teste.xlsx'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(current_dir, '../../files/test_files'))
NAME = 'composition_teste'
PACKAGE = DWSIMPackages.PengRobinson1978

# Optional DWSIM template must have one "Material Stream" and all required compounds;
# If provided a template, the 'PACKAGE' variable is ignored.
TEMPLATE: str | None = None #os.path.abspath(os.path.join(current_dir, '../../files/test_files/template.dwxmz'))

# Avoid burn rate and evaporation rate calculations.
DEBUG_MODE = False

# INPUT_FILE spreadsheet format.
FORMAT_TYPE = FormatType.DEFAULT

# Molar fraction phase to be output on the final file.
FRACTION_PHASE = PhaseType.OVERALL

# Which phase is active or inactive during @P&T flash.
PHASE_ACTIVITY = PhaseInput(Vapor=PhaseActivity.ACTIVE,
                            Liquid=PhaseActivity.ACTIVE)

# Compound basis to consider the input
BASIS = CompoundBasis.MOLE_FRAC

# Assigned unit only when applicable (MASS_FLOW or MOLE_FLOW)
BASIS_UNIT = BASIS.default_unit

# Type of operation made to filter output data.
OPERATION = OperationsFilter.CALORIFIC_VALUE

# Which phase type to filter (based on the filter operation; e.g., calorific, H2S/CO2, etc.).
PHASE_TYPE = PhaseType.OVERALL

# Use data previously present on INPUT_FILE or just use all simulated data.
ONLY_SIMULATED_VALUE = False

# Define logging level and if/where to write log file.
LOG_TYPE = logging.INFO
WRITE_LOGGER =  False
LOG_PATH = os.path.abspath(os.path.join(current_dir, '../../files/utils/composition_logs.log'))