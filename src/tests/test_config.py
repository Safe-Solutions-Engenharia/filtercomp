import os
import logging
from config import global_variables as cfg
from enums.dwsim_packages import DWSIMPackages
from enums.format_type import FormatType
from enums.filter_operations import (OperationsFilter, PhaseType, CompoundBasis)

def test_input_file_exists_or_path_resolves() -> None:
    assert isinstance(cfg.INPUT_FILE, str)
    assert cfg.INPUT_FILE.endswith("composicao_teste.xlsx")

def test_output_folder_path() -> None:
    assert isinstance(cfg.OUTPUT_FOLDER, str)
    assert os.path.basename(cfg.OUTPUT_FOLDER) == "test_files"

def test_enums_are_set_correctly() -> None:
    assert isinstance(cfg.PACKAGE, DWSIMPackages)
    assert cfg.PACKAGE == DWSIMPackages.PengRobinson1978

    assert isinstance(cfg.FORMAT_TYPE, FormatType)
    assert cfg.FORMAT_TYPE == FormatType.DEFAULT

    assert isinstance(cfg.OPERATION, OperationsFilter)
    assert cfg.OPERATION == OperationsFilter.CALORIFIC_VALUE

    assert isinstance(cfg.PHASE_TYPE, PhaseType)
    assert cfg.PHASE_TYPE == PhaseType.OVERALL

    assert isinstance(cfg.BASIS, CompoundBasis)
    assert cfg.BASIS == CompoundBasis.MOLE_FRAC

def test_log_settings() -> None:
    assert cfg.LOG_TYPE == logging.INFO
    assert isinstance(cfg.WRITE_LOGGER, bool)
    assert cfg.LOG_PATH.endswith("composition_logs.log")
