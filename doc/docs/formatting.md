# File Format Type

## Overview

This module defines classes and utilities for formatting data from Excel spreadsheets.

The key classes in this module are:

- `Format`: Abstract base class for formatting Excel sheets.

- `FormatFactory`: Factory to return the appropriate format class based on type.

---

## Create a New Format

To create a new data format, you need to follow three simple steps:

### 1. Declare the new format type

In `format_type.py`, extend the `FormatType` enum by adding a new entry.

```python title="format_type.py" linenums="3" hl_lines="3"
class FormatType(Enum):
    DEFAULT = 'Default'
    NEW_FORMAT = 'New_Format'
```

### 2. Implement the new format class

Create a new class in `format_files.py` that inherits from the base `Format` class. Override and customize the logic as needed.

```python title="format_files.py"
class FormatNewFormat(Format):
    def __init__(self, format_type: FormatType, data_dict: str) -> None:
        super().__init__(format_type, data_dict)
        self._format_dicts()
```
> You can define format-specific methods within this class to handle unique parsing rules or transformations.

### 3. Register the new format in the factory

Update the `FormatFactory` to include the new format class in its internal dictionary. This allows the factory to instantiate the correct class based on the format type.

```python title="format_files.py" linenums="228" hl_lines="5"
class FormatFactory:
    T = TypeVar('T', bound=Format)

    format_classes: dict[FormatType, type[Format]] = {
        FormatType.NEW_FORMAT: FormatNewFormat,
        FormatType.DEFAULT: FormatDefault
    }
```