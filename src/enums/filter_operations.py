from enum import Enum

class OperationsFilter(Enum):
    CALORIFIC_VALUE = 0
    CO2_AND_H2S_FRACTION = 1
    DISPERSION = 2

class PhaseType(Enum):
    OVERALL = 'Overall'
    VAPOR = 'Vapor'
    LIQUID1 = 'Liquid1'
    LIQUID2 = 'Liquid2'