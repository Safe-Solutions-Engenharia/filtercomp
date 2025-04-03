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
    MOLE_FRAC = 'Molar_Fractions'
    MASS_FRAC = 'Mass_Fractions'