import logging

from config.global_variables import (
    INPUT_FILE, OUTPUT_FOLDER, NAME, PACKAGE, DEBUG_MODE,
    FORMAT_TYPE, FRACTION_PHASE, BASIS, BASIS_UNIT, OPERATION, 
    PHASE_TYPE, ONLY_SIMULATED_VALUE, LOG_TYPE, WRITE_LOGGER, LOG_PATH
)
from utils.format_files import FormatFactory
from utils.operation_filter import FilterFactory
from utils.operations import FlashOperations
from utils.logger import custom_logger
from utils.file_saver import save_excel_file

def main() -> None:
    custom_logger.update_logger_settings(LOG_TYPE, write_logger=WRITE_LOGGER, 
                                         written_logger_path=LOG_PATH)

    full_df_dict, full_info_dict = FormatFactory.create_format(FORMAT_TYPE, INPUT_FILE).formated_data()

    flash_operations = FlashOperations(full_df_dict, full_info_dict,
                                      FRACTION_PHASE, BASIS, BASIS_UNIT, PACKAGE, debug_mode=DEBUG_MODE)

    flashed_df_dict = flash_operations.flashed_df_dict
    composition_dict = flash_operations.composition_dict

    filtered_data_dict = FilterFactory.create_filter(OPERATION, flashed_df_dict,
                                                    full_info_dict, composition_dict,
                                                    phase_type=PHASE_TYPE, use_simulated_value=ONLY_SIMULATED_VALUE).filtered_data_dict

    save_excel_file(OUTPUT_FOLDER, NAME, FRACTION_PHASE, filtered_data_dict)
    
    custom_logger.log('File saved successfully!', logging.INFO)

if __name__ == "__main__":
    main()
