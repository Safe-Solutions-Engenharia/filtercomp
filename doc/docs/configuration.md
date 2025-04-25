# Configurations

## Enums

**Enums** provide named symbolic constants, making the code more understandable and less error-prone.

### DWSIM Packages

Used to select the thermodynamic model from **DWSIM**, which governs how physical and chemical properties are calculated.

??? note "DWSIM Packages"
    ```python
    class DWSIMPackage(Enum):
        PengRobinson1978 = 'PengRobinson1978'
        ...
    ```

---

### Format Type

Used to standardize the input `.xlsx` file format to match the default output structure used during the processing phase.

??? note "Format Type"
    ```python
    class FormatType(Enum):
        DEFAULT = 'Default'
    ```

---

### Filter Operations

#### Operation Type

Defines types of operations that can be performed in the filtering phase.

??? note "Operations Filter"
    ```python
    class OperationsFilter(Enum):
        CALORIFIC_VALUE = 0
        CO2_AND_H2S_FRACTION = 1
        DISPERSION = 2
        CO2_FRACTION = 3
    ```

#### Phase Type

Represents the phase of the material stream: overall, vapor, oily, or aqueous.

??? note "Phase Type"
    ```python
    class PhaseType(Enum):
        OVERALL = 'Overall'
        VAPOR = 'Vapor'
        OIL = 'Liquid1'
        WATER = 'Liquid2'
    ```

#### Compound Basis

Defines the reference basis for compound data, with an associated default unit depending on the selected basis.

??? note "Compound Basis"
    ```python
    class CompoundBasis(Enum):
        MOLE_FRAC = 'MolarComposition'
        MASS_FRAC = 'MassComposition'
        MOLE_FLOW = 'CompoundMolarFlow'
        MASS_FLOW = 'CompoundMassFlow'

        @property
        def default_unit(self):
            return {
                CompoundBasis.MASS_FLOW: 'kg/h',
                CompoundBasis.MOLE_FLOW: 'kmol/h',
                CompoundBasis.MOLE_FRAC: None,
                CompoundBasis.MASS_FRAC: None,
            }.get(self, None)
    ```

#### Molar Flow Unit

Specifies the unit of measurement for molar flow, used when a different unit is required instead of the default.

??? note "Molar Flow Unit"
    ```python
    class MolarFlowUnit(Enum):
        KMOL_H = 'kmol/h'
        KMOL_S = 'kmol/s'
        MOL_S = 'mol/s'
    ```

#### Mass Flow Unit

Specifies the unit of measurement for mass flow, used when a different unit is required instead of the default.

??? note "Mass Flow Unit"
    ```python
    class MassFlowUnit(Enum):
        KG_H = 'kg/h'
        G_H = 'g/h'
        KG_S = 'kg/s'
    ```

---

## Global Variables
