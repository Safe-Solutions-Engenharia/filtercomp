import os
import logging
from config import global_variables as cfg
from enums.dwsim_packages import DWSIMPackages
from enums.format_type import FormatType
from enums.filter_operations import (OperationsFilter, PhaseType, CompoundBasis)

def test_input_file_exists_or_path_resolves() -> None:
    assert isinstance(cfg.INPUT_FILE, str)
    assert cfg.INPUT_FILE.endswith(".xlsx")

def test_config_are_set_correctly() -> None:
    assert isinstance(cfg.OUTPUT_FOLDER, str)

    assert isinstance(cfg.NAME, str)

    assert isinstance(cfg.DEBUG_MODE, bool)

    assert isinstance(cfg.PACKAGE, DWSIMPackages)

    assert isinstance(cfg.FORMAT_TYPE, FormatType)

    assert isinstance(cfg.OPERATION, OperationsFilter)

    assert isinstance(cfg.PHASE_TYPE, PhaseType)

    assert isinstance(cfg.BASIS, CompoundBasis)

    assert isinstance(cfg.ONLY_SIMULATED_VALUE, bool)

def test_log_settings() -> None:
    assert cfg.LOG_TYPE == logging.INFO
    assert isinstance(cfg.WRITE_LOGGER, bool)
    assert cfg.LOG_PATH.endswith("composition_logs.log")
