import logging
import os

from enums.dwsim_packages import DWSIMPackages
from enums.format_type import FormatType
from enums.filter_operations import OperationsFilter, PhaseType

current_dir = os.path.dirname(__file__) 

INPUT_FILE = os.path.abspath(os.path.join(current_dir, '../../tests/composicao_teste.xlsx'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(current_dir, '../../tests'))
NAME = 'composition_teste'
PACKAGE = DWSIMPackages.PengRobinson1978

# Avoid burn rate calculations.
DEBUG_MODE = False

# INPUT_FILE spreadsheet format.
FORMAT_TYPE = FormatType.DEFAULT

# Molar fraction phase to be output on the final file.
# Read LIQUID1 as Oil and LIQUID2 as Water.
FRACTION_PHASE = PhaseType.OVERALL

# Type of operation made to filter data.
OPERATION = OperationsFilter.CALORIFIC_VALUE

# Which phase type to filter.
# Read LIQUID1 as Oil and LIQUID2 as Water.
PHASE_TYPE = PhaseType.OVERALL

# Use data previously present on INPUT_FILE or just use all simulated data.
ONLY_SIMULATED_VALUE = False

# Define logging level and if/where to write log file.
LOG_TYPE = logging.INFO
WRITE_LOGGER =  False
LOG_PATH = os.path.abspath(os.path.join(current_dir, '../../files/utils/composition_logs.log'))
