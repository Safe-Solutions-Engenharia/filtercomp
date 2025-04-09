from enum import Enum

class OperationsFilter(Enum):
    CALORIFIC_VALUE = 0
    CO2_AND_H2S_FRACTION = 1
    DISPERSION = 2

class PhaseType(Enum):
    OVERALL = 'Overall'
    VAPOR = 'Vapor'
    OIL = 'Liquid1'
    WATER = 'Liquid2'

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

class MolarFlowUnit(Enum):
    KMOL_H = 'kmol/h'
    KMOL_S = 'kmol/s'
    MOL_S = 'mol/s'

class MassFlowUnit(Enum):
    KG_H = 'kg/h'
    G_H = 'g/h'
    KG_S = 'kg/s'