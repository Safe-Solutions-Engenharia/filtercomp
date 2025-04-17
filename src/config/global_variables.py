import logging
import os

from enums.dwsim_packages import DWSIMPackages
from enums.format_type import FormatType
from enums.filter_operations import (OperationsFilter, PhaseType, CompoundBasis, 
                                     MolarFlowUnit, MassFlowUnit)

current_dir = os.path.dirname(__file__) 

INPUT_FILE = os.path.abspath(os.path.join(current_dir, '../../files/test_files/composicao_teste.xlsx'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(current_dir, '../../files/test_files'))
NAME = 'composition_teste'
PACKAGE = DWSIMPackages.PengRobinson1978

# Avoid burn rate and evaporation rate calculations.
DEBUG_MODE = False

# INPUT_FILE spreadsheet format.
FORMAT_TYPE = FormatType.DEFAULT

# Molar fraction phase to be output on the final file.
FRACTION_PHASE = PhaseType.OVERALL

# Compound basis to consider the input
BASIS = CompoundBasis.MOLE_FRAC

# Assigned unit only when applicable (MASS_FLOW or MOLE_FLOW)
BASIS_UNIT = BASIS.default_unit

# Type of operation made to filter data.
OPERATION = OperationsFilter.CALORIFIC_VALUE

# Which phase type to filter.
PHASE_TYPE = PhaseType.OVERALL

# Use data previously present on INPUT_FILE or just use all simulated data.
ONLY_SIMULATED_VALUE = False

# Define logging level and if/where to write log file.
LOG_TYPE = logging.INFO
WRITE_LOGGER =  False
LOG_PATH = os.path.abspath(os.path.join(current_dir, '../../files/utils/composition_logs.log'))