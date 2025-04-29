# Operation Filters

## Overview

This module defines classes and utilities for filtering data based on specific criteria. It processes each row of a dataframe, compares the relevant values, and selects the highest value according to the defined filter conditions.

---

## Calorific Value

The **Calorific Value** is calculated by combining:

* The **composition** of the fluid phase,
* The **heat of combustion** of each individual component,
* The **molar** flow rate of the phase.

The **Calorific Value** is computed as:

$$
\text{Calorific Value} \left(\frac {kJ}{h} \right) = \left[ \sum_{i} \left( H_i \cdot x_i \right) \right] \cdot \dot{n}
$$

Where:

- \( H_i \) =  **Heat of combustion** of component \(i\) \((\text{kJ/kmol})\)
- \( x_i \) = **Molar fraction** (or relative molar contribution) of component \(i\)
- \( \dot{n} \) = **Total molar flow rate** of the phase \((\text{kmol/h})\)

---

## CO₂ and H₂S Fraction

This class filters data based on the **CO₂ and H₂S molar fractions**. It processes each row of the input dataframes, identifies the maximum values for CO₂ and H₂S according to specific conditions, and selects the scenario that best meets the defined criteria.

If the scenarios corresponding to the maximum CO₂ and H₂S values are different, the module compares their molecular weights: if the values are similar, the CO₂ and H₂S data are merged into a single stream; if they differ significantly, both streams are selected independently.

---

## CO₂ Fraction

This class filters data based on the **CO₂ molar fraction**. It processes the input dataframes, identifies the scenario with the highest CO₂ content for each current, and selects the corresponding data.

---


## Create a New Filter

To create a new filter, you need to follow three simple steps:

### 1. Declare the new filter type

In `filter_operations.py`, extend the `OperationFilter` enum by adding a new entry.

```python title="filter_operations.py" linenums="3" hl_lines="5"
class OperationsFilter(Enum):
    CALORIFIC_VALUE = 0
    CO2_AND_H2S_FRACTION = 1
    CO2_FRACTION = 3
    NEW_FILTER = 4
```

### 2. Implement the new filter class

Create a new class in `operation_filter.py` that inherits from the base `Filter` class. Override and customize the logic as needed.

```python title="operation_filter.py"
class NewFilter(Filter):
    def __init__(self, 
                 filter_type: OperationsFilter,
                 flashed_df_dict: dict[str, pd.DataFrame], 
                 full_info_dict: dict[str, pd.DataFrame],
                 composition_dict: dict[str, dict[str, list[float]]],
                 phase_type: PhaseType,
                 use_simulated_value: bool) -> None:
        super().__init__(filter_type,
                         flashed_df_dict, 
                         full_info_dict,
                         composition_dict,
                         phase_type,
                         use_simulated_value)
```
> You can define methods within this class to handle unique parsing rules or transformations.

### 3. Register the new filter in the factory

Update the `FilterFactory` to include the new filter class in its internal dictionary. This allows the factory to instantiate the correct class based on the filter type.

```python title="operation_filter.py" linenums="305" hl_lines="8"
class FilterFactory:
    T = TypeVar('T', bound=Filter)

    filter_classes: dict[OperationsFilter, type[Filter]] = {
        OperationsFilter.CALORIFIC_VALUE: CalorificValue,
        OperationsFilter.CO2_AND_H2S_FRACTION: CO2AndH2SFraction,
        OperationsFilter.CO2_FRACTION: CO2Fraction,
        OperationsFilter.NEW_FILTER: NewFilter
    }
```