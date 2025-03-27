# General Information

## Input File Format

You can define a new input format by creating a corresponding type in [format_files.py](/src/utils/format_files.py) and adding its name as an enum in [format_type.py](/src/enums/format_type.py). Just make sure to maintain the standard format for the output.

## Filter operations

Similarly, to implement a new scenario filtering method, add a new class in [operations_filter.py](/src/utils/operation_filter.py) and register its name in the enum defined in [filter_operations.py](/src/enums/filter_operations.py).