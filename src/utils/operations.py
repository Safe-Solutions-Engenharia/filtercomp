import logging
import os
from collections import OrderedDict
import sqlite3
import difflib

from chemicals import Tc, Pc, CAS_from_any, Tb, MW
from chemicals.phase_change import Riedel
import numpy as np
from tqdm import tqdm
import pandas as pd
import clr

from enums.dwsim_packages import DWSIMPackages
from enums.filter_operations import PhaseType, CompoundBasis
from utils.logger import custom_logger

DWSIMPATH = os.path.join(os.getenv('USERPROFILE'), "AppData", "Local", "DWSIM")
if not os.path.exists(DWSIMPATH):
    custom_logger.log('DWSIM 9 not found!', logging.ERROR)
    raise FileNotFoundError('Download DWSIM v9 to finish the operation!')

clr.AddReference(os.path.join(DWSIMPATH, "DWSIM.Automation.dll"))
clr.AddReference(os.path.join(DWSIMPATH, "DWSIM.Interfaces.dll"))
clr.AddReference(os.path.join(DWSIMPATH, "DWSIM.Thermodynamics.dll"))
clr.AddReference(os.path.join(DWSIMPATH, "DWSIM.Thermodynamics.ThermoC.dll"))

from System.IO import Directory # type: ignore
from System import Array, Double # type: ignore
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType # type: ignore
from DWSIM.Interfaces import IFlowsheet # type: ignore
from DWSIM.Automation import Automation3 # type: ignore
from DWSIM.Interfaces.Enums import FlashSetting, ForcedPhase # type: ignore
from DWSIM.Thermodynamics import PropertyPackages # type: ignore

class FlashOperations:
    def __init__(self, 
                 full_df_dict: dict[str, pd.DataFrame], 
                 full_info_dict: dict[str, pd.DataFrame],
                 molar_phase: PhaseType,
                 compound_basis: CompoundBasis,
                 package: DWSIMPackages,
                 *,
                 debug_mode: bool = False) -> None:
        
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_filename = 'heat_of_combustion.db'
        self.database_path = os.path.join(base_path, 'files', 'database', db_filename)
        self.molar_phase = molar_phase.value
        self.compound_basis = compound_basis.value
        self.debug_mode = debug_mode

        self.HEADERS: dict[str, list[str]] = {'SCENARIO': ['Cenário'],
                        'OVERALL': ['Temperature', 'Pressure', 'Molar Flow', 'Mass Flow', 'Cp/Cv @T&P Cond', 'Molecular Weight @T&P Cond', 'Burn Rate', 
                                    'Evaporation Rate'],
                        'VAPOUR PHASE': ['Molar Flow @Std Cond', 'Vol Flow @T&P Cond', 'Vol Flow @Std Cond','Mass Fraction',
                                         'Density @T&P Cond', 'Density @Std Cond', 'Molecular Weight @T&P Cond',
                                         'Molecular Weight @Std Cond','Z Factor @T&P Cond', 'Z Factor @Std Cond'],
                        'LIQUID PHASE': ['Molar Flow @Std Cond', 'Vol Flow @T&P Cond', 'Vol Flow @Std Cond',
                                        'Mass Fraction', 'Molecular Weight @Std Cond', 'Molecular Weight @T&P Cond'],
                        'OILY PHASE': ['Molar Flow @Std Cond', 'Vol Flow @T&P Cond', 'Vol Flow @Std Cond',
                                        'Mass Fraction', 'Density @T&P Cond', 'Density @Std Cond', 'Molecular Weight @Std Cond', 'Molecular Weight @T&P Cond']}
        
        self.name_convention: dict[str, str] = {'Isobutane': 'i-Butane',
                                                '2-methyl-1-butene': '2-Methyl-Butane',
                                                'Isopentane': 'i-Pentane',
                                                'N-pentane': 'n-Pentane',
                                                'N-hexane': 'Hexane',
                                                'N-heptane': 'Heptane',
                                                'N-octane': 'Octane',
                                                'N-nonane': 'Nonane',
                                                'N-decane': 'Decane',
                                                'N-undecane': 'Undecane',
                                                'N-dodecane': 'Dodecane',
                                                'N-tridecane': 'Tridecane',
                                                'N-tetradecane': 'Tetradecane',
                                                'N-pentadecane': 'Pentadecane',
                                                'N-hexadecane': 'Hexadecane',
                                                'N-heptadecane': 'Heptadecane',
                                                'N-octadecane': 'Octadecane',
                                                'N-nonadecane': 'Nonadecane',
                                                'N-heptacosane': 'C20+',
                                                'N-nonacosane': 'C20++'}
        
        self.full_df_dict = full_df_dict
        self.full_info_dict = full_info_dict
        self.package = package.value
        self.composition_dict: dict[str, dict[str, dict[str, list[float]]]] = {}
        self.flashed_df_dict: dict[str, pd.DataFrame] = self.dwsim_main_flash_operation(self.full_df_dict)

        self.mod_header = None
        self.old_header = None

    def replace_compound_names_dataframe(self, compound_df: pd.DataFrame) -> pd.DataFrame:
        for col in compound_df.columns:
            if col in self.name_convention.values():
                key = next(k for k, v in self.name_convention.items() if v == col)
                compound_df.rename(columns={col: key}, inplace=True)
        
        return compound_df

    #TODO: Adjust the 'force phase' relation.
    def flash_operation(self,
                        component_list: list[float], pressure_Pa: float, 
                        temperature_K: float, flow_rate_name: str, pressure_unit: str,
                        flow_rate: float, gas_flow: float,
                        liquid_flow: float, flash_type: str) -> None:
        component_list = [float(comp) for comp in component_list]
        getattr(self.mst, f"SetOverall{self.compound_basis}")(Array[Double](component_list))
        self.mst.SetFlashSpec("PT")
        self.mst.SetPressure(f'{pressure_Pa} {pressure_unit}')
        self.mst.SetTemperature(f'{temperature_K} K')

        flow_types = {'overall_mass flow': [' kg/h', 'SetMassFlow'],
                      'overall_molar flow': [' kmol/h', 'SetMolarFlow'],
                      'overall_volumetric flow': [' m3/h', 'SetVolumetricFlow']}
        flow_functions = flow_types[flow_rate_name]
        getattr(self.mst, flow_functions[1])(flow_rate + flow_functions[0])

        if flash_type == 'Flash @P&T':
            if not gas_flow:
                self.mst.ForcePhase = ForcedPhase.Liquid
            elif not liquid_flow:
                self.mst.ForcePhase = ForcedPhase.Vapor
            else:
                self.mst.ForcePhase = ForcedPhase.GlobalDef
        else:
            self.mst.ForcePhase = ForcedPhase.GlobalDef

        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = "1E-9"
        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = "1E-9"

        tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
        success = False
        while not success:
            try:
                if tol_val >= 1E-2:
                    break
                self.mst.Calculate()
                success = True
            except Exception as e:
                num_iter = int(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations])
                tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
                if num_iter < 1000:
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = str(num_iter + 50)
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = str(num_iter + 50)
                else:
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = str(tol_val * 10)
                    self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = str(tol_val * 10)
                continue

        if not success:
            custom_logger.log(f'Erro no {flash_type} do cenario {self.cen_name} da corrente {self.current_name}', logging.ERROR)

    @staticmethod
    def get_compound_name(current_value: pd.DataFrame, 
                          flowsheet: IFlowsheet) -> dict[str, any]:
        compound_names = [x.lower() for x in current_value][7:]
        compound_index = {name.lower(): index for index, name in enumerate(compound_names)}

        compound_dict = {}
        for compound in flowsheet.AvailableCompounds:
            if compound.Key.lower() in compound_index:
                index = compound_index[compound.Key.lower()]
                compound_dict[index] = compound

        compound_dict = OrderedDict(sorted(compound_dict.items()))
        
        return compound_dict

    @staticmethod
    def get_compound_value(current_value: pd.DataFrame, cen_name: str) -> list[float]:
        compound_list = current_value[current_value['SCENARIO_Cenário'] == cen_name].iloc[0, 7:].to_list()
        compound_list = [x / 100 if sum(compound_list) > 2 else x for x in compound_list]

        return compound_list

    def dataframe_base(self, current_value: pd.DataFrame) -> pd.DataFrame:
        df = pd.DataFrame()

        for key, values in self.HEADERS.items():
            for value in values:
                df.loc[0, f"{key}_{value}"] = key

        for values2 in current_value.columns[7:]:
            df.loc[0, values2] = 'COMPONENT FRACTION'

        return df

    def get_overall_data(self,
                        scenario_dict: dict[str, float]) -> dict[str, float]:
        mass_flow_overall = self.mst.GetPhase('Overall').Properties.massflow * 3600 #kg/h
        molar_flow_overall = self.mst.GetPhase('Overall').Properties.molarflow * 3.6 #kmol/h
        cp_vapor = self.mst.GetPhase('Overall').Properties.heatCapacityCp
        cv_vapor = self.mst.GetPhase('Overall').Properties.heatCapacityCv
        cp_sobre_cv = cp_vapor / cv_vapor if cp_vapor and cv_vapor else np.nan
        molecular_weight_overall = self.mst.GetPhase('Overall').Properties.molecularWeight
        
        scenario_dict.update({
            'OVERALL_Molar Flow': molar_flow_overall,
            'OVERALL_Mass Flow': mass_flow_overall,
            'OVERALL_Cp/Cv @T&P Cond': cp_sobre_cv,
            'OVERALL_Molecular Weight @T&P Cond': molecular_weight_overall,
        })
        
        return scenario_dict
    
    def get_misc_properties(self,
                            liquid1: str, 
                            liquid2: str) -> tuple[float]:
        MOLAR_FLOW_CONVERSION = 3.6
        VOLUMETRIC_FLOW_CONVERSION = 3600
        
        phase1 = self.mst.GetPhase(liquid1).Properties
        phase2 = self.mst.GetPhase(liquid2).Properties
        
        volumetric_flow_liquid1 = phase1.volumetric_flow * VOLUMETRIC_FLOW_CONVERSION if phase1.volumetric_flow else phase1.volumetric_flow
        volumetric_flow_liquid2 = phase2.volumetric_flow * VOLUMETRIC_FLOW_CONVERSION if phase2.volumetric_flow else phase2.volumetric_flow
        
        if volumetric_flow_liquid1 and volumetric_flow_liquid2:
            volumetric_flow_liquid2 = volumetric_flow_liquid1 + volumetric_flow_liquid2
        elif volumetric_flow_liquid1:
            volumetric_flow_liquid2 = volumetric_flow_liquid1

        molecular_weight_oil = phase1.molecularWeight
        mass_fraction_oil = phase1.massfraction
        molar_flow_oil = phase1.molarflow * MOLAR_FLOW_CONVERSION if phase1.molarflow else phase1.molarflow
        
        molecular_weight_water = phase2.molecularWeight
        mass_fraction_water = phase2.massfraction
        molar_flow_water = phase2.molarflow * MOLAR_FLOW_CONVERSION if phase2.molarflow else phase2.molarflow
        
        return (
            volumetric_flow_liquid1, volumetric_flow_liquid2,
            molecular_weight_oil, molecular_weight_water,
            mass_fraction_oil, mass_fraction_water,
            molar_flow_oil, molar_flow_water
        )
    
    def get_pt_flash_data(self,
                          scenario_dict: dict[str, float]) -> dict[str, float]:
        # Vapor
        volumetric_flow_vapor = self.mst.GetPhase('Vapor').Properties.volumetric_flow * 3600 if self.mst.GetPhase(
            'Vapor').Properties.volumetric_flow else self.mst.GetPhase('Vapor').Properties.volumetric_flow
        z_factor_vapor = self.mst.GetPhase('Vapor').Properties.compressibilityFactor
        molecular_weight_vapor = self.mst.GetPhase('Vapor').Properties.molecularWeight
        density_vapor = self.mst.GetPhase('Vapor').Properties.density

        # Liquid (Oil + Water)
        mass_fraction_liquid2 = self.mst.GetPhase('Liquid2').Properties.massfraction
        density_oil = self.mst.GetPhase('Liquid1').Properties.density if self.mst.GetPhase(
            'Liquid1').Properties.density else 0
        molecular_weight_oil = self.mst.GetPhase('Liquid1').Properties.molecularWeight if self.mst.GetPhase(
            'Liquid1').Properties.molecularWeight else 0
        
        if mass_fraction_liquid2 and (890 > density_oil or density_oil > 1500) and (17 > molecular_weight_oil or molecular_weight_oil > 19):
            volumetric_flow_oil, volumetric_flow_liquid, molecular_weight_oil, molecular_weight_water, _, _, _, _ = self.get_misc_properties('Liquid1', 'Liquid2')
        else:
            if mass_fraction_liquid2:
                volumetric_flow_oil, volumetric_flow_liquid, molecular_weight_oil, molecular_weight_water, _, _, _, _ = self.get_misc_properties('Liquid2', 'Liquid1')
            elif density_oil is not None and (890 < density_oil < 1500 and 17 < molecular_weight_oil < 19):
                volumetric_flow_oil, volumetric_flow_liquid, molecular_weight_oil, molecular_weight_water, _, _, _, _ = self.get_misc_properties('Liquid2', 'Liquid1')
                density_oil = self.mst.GetPhase('Liquid2').Properties.density if self.mst.GetPhase(
                    'Liquid2').Properties.density else 0
            else:
                volumetric_flow_oil, volumetric_flow_liquid, molecular_weight_oil, molecular_weight_water, _, _, _, _ = self.get_misc_properties('Liquid1', 'Liquid2')
    
        scenario_dict.update({
            'VAPOUR PHASE_Vol Flow @T&P Cond': volumetric_flow_vapor,
            'VAPOUR PHASE_Density @T&P Cond': density_vapor,
            'VAPOUR PHASE_Molecular Weight @T&P Cond': molecular_weight_vapor,
            'VAPOUR PHASE_Z Factor @T&P Cond': z_factor_vapor,
            'OILY PHASE_Vol Flow @T&P Cond': volumetric_flow_oil,
            'OILY PHASE_Density @T&P Cond': density_oil,
            'OILY PHASE_Molecular Weight @T&P Cond': molecular_weight_oil,
            'LIQUID PHASE_Vol Flow @T&P Cond': volumetric_flow_liquid,
            'LIQUID PHASE_Molecular Weight @T&P Cond': molecular_weight_water,
        })

        return scenario_dict

    def get_overall_enthalpies(self) -> tuple[float, float]:
        value_liquid1 = self.mst.GetPhase('Liquid1').Compounds
        liquid1_list_mf = [value_liquid1[key].MassFraction if value_liquid1[key].MassFraction is not None else 0 for key in value_liquid1.Keys]
        compound_names = [key for key in value_liquid1.Keys]

        conn = sqlite3.connect(self.database_path)
        query = "SELECT * FROM table_name;"
        enthalpy_db = pd.read_sql(query, conn)
        conn.close()

        overall_vaporization_enthalpy = 0
        overall_combustion_enthalpy = 0
        for comp_index, comp_value in enumerate(compound_names):
            cas = CAS_from_any(comp_value[2:] if comp_value.startswith('N-') else comp_value)
            critical_temperature, boiling_temperature, critical_pressure = Tc(cas), Tb(cas), Pc(cas)
            vaporization_enthalpy = Riedel(boiling_temperature, critical_temperature, critical_pressure) # J/mol > kJ/kmol

            mol_weight = MW(cas) # mol/g > kmol/kg
            vaporization_enthalpy_kj_kg = vaporization_enthalpy / mol_weight # J/mol * mol/g = J/g > kJ/kg
            overall_vaporization_enthalpy += vaporization_enthalpy_kj_kg * liquid1_list_mf[comp_index]

            if comp_value in enthalpy_db['Composition'].values:
                combustion_enthalpy = enthalpy_db[enthalpy_db['Composition'] == comp_value]['Enthalpy'].values[0] #kJ/kmol
                combustion_enthalpy_kj_kg = combustion_enthalpy / mol_weight # kJ/kg
                overall_combustion_enthalpy += combustion_enthalpy_kj_kg * liquid1_list_mf[comp_index]
        
        return overall_vaporization_enthalpy, overall_combustion_enthalpy
    
    # TODO: refactor this a bit.
    def refine_bubble_point(self, release_temperature: float) -> float:
        vapor_fraction = 0
        index_temperature = 0
        fast_resume = False
        save_temperature = self.mst.GetPhase('Overall').Properties.temperature
        save_pressure = self.mst.GetPhase('Overall').Properties.pressure
        save_flow = self.mst.GetPhase('Overall').Properties.molarflow

        while vapor_fraction < 1:
            success = False

            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = "1E-9"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = "1E-9"

            tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
            while not success:
                try:
                    if tol_val >= 1E-2:
                        break
                    self.mst.SetTemperature(f'{release_temperature + index_temperature} K')
                    self.mst.Calculate()
                    vapor_fraction = self.mst.GetPhase('Vapor').Properties.molarfraction if self.mst.GetPhase('Vapor').Properties.molarfraction else 0
                    success = True
                except Exception as e:
                    num_iter = int(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations])
                    tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
                    if num_iter < 1000:
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = str(num_iter + 100)
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = str(num_iter + 100)
                    else:
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = str(tol_val * 10)
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = str(tol_val * 10)
                    continue
            
            if not success:
                custom_logger.log(f'Erro na etapa geral do cálculo de burn rate do cenario {self.cen_name} da corrente {self.current_name}. '
                                  f'Aumentando a temperatura de {release_temperature + index_temperature} para {release_temperature + index_temperature + 50} e tentando novamente...\n', 
                                  logging.ERROR)

            if vapor_fraction < 1:
                index_temperature += 50

        refinement_step = 1  # Smaller step for refining
        while vapor_fraction >= 1:
            index_temperature -= refinement_step  # Decrease temperature
            success = False

            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = "1E-9"
            self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = "1E-9"

            tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
            while not success:
                try:
                    if tol_val >= 1E-2:
                        break
                    self.mst.SetTemperature(f'{release_temperature + index_temperature} K')
                    self.mst.Calculate()
                    vapor_fraction = self.mst.GetPhase('Vapor').Properties.molarfraction if self.mst.GetPhase('Vapor').Properties.molarfraction else 0
                    success = True  # Calculation succeeded
                except Exception as e:
                    num_iter = int(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations])
                    tol_val = float(self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance])
                    if num_iter < 1000:
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = str(num_iter + 100)
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = str(num_iter + 100)
                    else:
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_External_Iterations] = "100"
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Maximum_Number_Of_Internal_Iterations] = "100"
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_External_Loop_Tolerance] = str(tol_val * 10)
                        self.instantiated_package.FlashSettings[FlashSetting.PTFlash_Internal_Loop_Tolerance] = str(tol_val * 10)
                    continue

                if not vapor_fraction and not fast_resume:
                    index_temperature -= refinement_step
                    success = False
                    fast_resume = True

            if not success:
                custom_logger.log(f'Erro na etapa de refinamento cálculo de burn rate do cenario {self.cen_name} da corrente {self.current_name}.' 
                                  f'Decrescendo temperatura de {release_temperature + index_temperature} para {release_temperature + index_temperature - refinement_step} e tentando novamente...\n', 
                                  logging.ERROR)

        self.mst.SetPressure(save_pressure)
        self.mst.SetTemperature(save_temperature)
        self.mst.SetMolarFlow(save_flow)

        return index_temperature

    def get_burn_rate(self,
                      mass_fraction_liquid2_std: float,
                      molecular_weight_oil: float) -> tuple[float, float, float, float]:
        
        rho_density = self.mst.GetPhase('Liquid1').Properties.density if self.mst.GetPhase(
                'Liquid1').Properties.density else 0
        
        if mass_fraction_liquid2_std:
            cp_std = self.mst.GetPhase('Liquid1').Properties.heatCapacityCp
        else:
            if not (890 < rho_density < 1500) and not (17 < molecular_weight_oil < 19) and rho_density != 0:
                cp_std = self.mst.GetPhase('Liquid1').Properties.heatCapacityCp
            else:
                cp_std = 0.0
                rho_density = 0.0

        overall_vaporization_enthalpy, overall_combustion_enthalpy = self.get_overall_enthalpies() if rho_density else (1.0, 1.0)
        index_temperature = self.refine_bubble_point(298.15) if rho_density else 1.0

        constante_val = 1.27E-6

        burn_rate = constante_val * rho_density * ((overall_combustion_enthalpy)/(
                    overall_vaporization_enthalpy + cp_std * (index_temperature))) # kg/(m²*s)
        
        burn_rate = abs(burn_rate) if burn_rate else -1.0

        return burn_rate, overall_vaporization_enthalpy, rho_density
    
    def get_evaporation_rate_and_evaporation_fraction(self, 
                                                      overall_vaporization_enthalpy: float,
                                                      release_temperature: float, rho_density: float) -> tuple[float, float]:
        
        constante_val = 10.5

        index_temperature = self.refine_bubble_point(release_temperature) if rho_density else 0.0

        converted_overall_vaporization_enthalpy = overall_vaporization_enthalpy * 1000 #J/kg

        evaporation_rate = constante_val * ((index_temperature)/(converted_overall_vaporization_enthalpy)) # kg/(m²*s)
        
        evaporation_rate = abs(evaporation_rate) if evaporation_rate else -1.0

        return evaporation_rate

    def get_std_flash_data(self, 
                          scenario_dict: dict[str, float],
                          release_temperature: float) -> dict[str, float]:
        # Vapor
        mass_fraction_vapor_std = self.mst.GetPhase('Vapor').Properties.massfraction
        molar_flow_vapor_std = self.mst.GetPhase('Vapor').Properties.molarflow * 3.6 if self.mst.GetPhase(
            'Vapor').Properties.molarflow else self.mst.GetPhase('Vapor').Properties.molarflow
        volumetric_flow_vapor_std = self.mst.GetPhase('Vapor').Properties.volumetric_flow * 3600 if self.mst.GetPhase(
            'Vapor').Properties.volumetric_flow else self.mst.GetPhase('Vapor').Properties.volumetric_flow
        density_vapor_std = self.mst.GetPhase('Vapor').Properties.density
        molecular_weight_vapor_std = self.mst.GetPhase('Vapor').Properties.molecularWeight
        z_factor_vapor_std = self.mst.GetPhase('Vapor').Properties.compressibilityFactor

        # Liquid (Oil + Water)
        mass_fraction_liquid2_std = self.mst.GetPhase('Liquid2').Properties.massfraction
        density_oil_std = self.mst.GetPhase('Liquid1').Properties.density if self.mst.GetPhase(
            'Liquid1').Properties.density else 0
        molecular_weight_oil = self.mst.GetPhase('Liquid1').Properties.molecularWeight if self.mst.GetPhase(
            'Liquid1').Properties.molecularWeight else 0
        
        if mass_fraction_liquid2_std and (890 > density_oil_std or density_oil_std > 1500) and (17 > molecular_weight_oil or molecular_weight_oil > 19):
            (volumetric_flow_oil, volumetric_flow_liquid,
            molecular_weight_oil_std, molecular_weight_water_std,
            mass_fraction_oil_std, mass_fraction_water_std,
            molar_flow_oil_std, molar_flow_water_std) = self.get_misc_properties('Liquid1', 'Liquid2')

        else:
            if mass_fraction_liquid2_std:
                (volumetric_flow_oil, volumetric_flow_liquid,
                molecular_weight_oil_std, molecular_weight_water_std,
                mass_fraction_oil_std, mass_fraction_water_std,
                molar_flow_oil_std, molar_flow_water_std) = self.get_misc_properties('Liquid2', 'Liquid1')
            elif density_oil_std is not None and (890 < density_oil_std < 1500 and 17 < molecular_weight_oil < 19):
                (volumetric_flow_oil, volumetric_flow_liquid,
                molecular_weight_oil_std, molecular_weight_water_std,
                mass_fraction_oil_std, mass_fraction_water_std,
                molar_flow_oil_std, molar_flow_water_std) = self.get_misc_properties('Liquid2', 'Liquid1')
                density_oil_std = self.mst.GetPhase('Liquid2').Properties.density if self.mst.GetPhase(
                'Liquid2').Properties.density else 0
            else:
                (volumetric_flow_oil, volumetric_flow_liquid,
                molecular_weight_oil_std, molecular_weight_water_std,
                mass_fraction_oil_std, mass_fraction_water_std,
                molar_flow_oil_std, molar_flow_water_std) = self.get_misc_properties('Liquid1', 'Liquid2')

        # Burn rate (Oil)
        if not self.debug_mode:
            burn_rate, overall_vaporization_enthalpy, rho_density = self.get_burn_rate(mass_fraction_liquid2_std, 
                                                                          molecular_weight_oil)
            
            evaporation_rate = self.get_evaporation_rate_and_evaporation_fraction(overall_vaporization_enthalpy, 
                                                                                  release_temperature, rho_density)
        else:
            burn_rate = 0
            evaporation_rate = (0, 0)

        scenario_dict.update({
            'OVERALL_Burn Rate': burn_rate,
            'OVERALL_Evaporation Rate': evaporation_rate,
            'VAPOUR PHASE_Mass Fraction': mass_fraction_vapor_std,
            'VAPOUR PHASE_Molar Flow @Std Cond': molar_flow_vapor_std,
            'VAPOUR PHASE_Vol Flow @Std Cond': volumetric_flow_vapor_std,
            'VAPOUR PHASE_Density @Std Cond': density_vapor_std,
            'VAPOUR PHASE_Molecular Weight @Std Cond': molecular_weight_vapor_std,
            'VAPOUR PHASE_Z Factor @Std Cond': z_factor_vapor_std,
            'LIQUID PHASE_Vol Flow @Std Cond': volumetric_flow_liquid,
            'LIQUID PHASE_Mass Fraction': mass_fraction_water_std,
            'LIQUID PHASE_Molecular Weight @Std Cond': molecular_weight_water_std,
            'LIQUID PHASE_Molar Flow @Std Cond': molar_flow_water_std,
            'OILY PHASE_Vol Flow @Std Cond': volumetric_flow_oil,
            'OILY PHASE_Density @Std Cond': density_oil_std,
            'OILY PHASE_Mass Fraction': mass_fraction_oil_std,
            'OILY PHASE_Molecular Weight @Std Cond': molecular_weight_oil_std,
            'OILY PHASE_Molar Flow @Std Cond': molar_flow_oil_std,
        })

        return scenario_dict
    
    def get_compounds_molar_fraction(self, scenario_dict: dict[str, float],
                                    compound_list: list[str],
                                    current_value: pd.DataFrame) -> dict[str, float]:

        for x in range(len(compound_list), 0, -1):
            scenario_dict.update({
            current_value.columns[-x]: compound_list[-x],
            })

        return scenario_dict
    
    @staticmethod
    def get_scenario_dataframe(dataframe_base: pd.DataFrame, 
                               scenario_dict: dict[str, float]) -> pd.DataFrame:
        column_order = dataframe_base.columns.tolist()
        ordered_dict = {key: [scenario_dict[key]] for key in column_order}

        df = pd.DataFrame(ordered_dict)

        return df

    def get_compound_value_after_flash(self, compoud_dict: dict[str, any]) -> list[float]:
        comp_phase = self.mst.GetPhase(self.molar_phase).Compounds

        density_liquid1 = self.mst.GetPhase('Liquid1').Properties.density

        if self.molar_phase == 'Liquid1':
            if density_liquid1 is not None and 890 < density_liquid1 < 1500:
                comp_phase = self.mst.GetPhase('Liquid2').Compounds
            else:
                comp_phase = self.mst.GetPhase(self.molar_phase).Compounds

        elif self.molar_phase == 'Liquid2':
            if density_liquid1 is not None and 890 < density_liquid1 < 1500:
                comp_phase = self.mst.GetPhase('Liquid1').Compounds
            else:
                comp_phase = self.mst.GetPhase(self.molar_phase).Compounds

        composition_list = [comp_phase[x.Key].MoleFraction for x in compoud_dict.values()]
        return composition_list
    
    def get_all_compound_value(self, compoud_dict: dict[str, any]) -> None:
        self.current_comp_dict: dict[str, list[float]] = {}
        for phase_type in PhaseType:
            phase = self.mst.GetPhase(phase_type.value)
            comp_phase = phase.Compounds

            if phase_type.value == 'Liquid1' or phase_type.value == 'Liquid2':
                density_liquid1 = self.mst.GetPhase('Liquid1').Properties.density

                liquid1_comp = self.mst.GetPhase('Liquid1').Compounds
                liquid2_comp = self.mst.GetPhase('Liquid2').Compounds

                if density_liquid1 is not None and 890 < density_liquid1 < 1500:
                    comp_list_oil = [liquid2_comp[x.Key].MoleFraction for x in compoud_dict.values()]
                    comp_list_water = [liquid1_comp[x.Key].MoleFraction for x in compoud_dict.values()]
                else:
                    comp_list_oil = [liquid1_comp[x.Key].MoleFraction for x in compoud_dict.values()]
                    comp_list_water = [liquid2_comp[x.Key].MoleFraction for x in compoud_dict.values()]

                self.current_comp_dict['Liquid1'] = comp_list_oil
                self.current_comp_dict['Liquid2'] = comp_list_water
            else:
                comp_list = [comp_phase[x.Key].MoleFraction for x in compoud_dict.values()]
                self.current_comp_dict[phase_type.value] = comp_list

    def operations_per_scenario(self, current_name: str, current_value: pd.DataFrame) -> pd.DataFrame:
        self.current_name = current_name
        dataframe_base = self.dataframe_base(current_value)

        for cen_name in tqdm(current_value['SCENARIO_Cenário'], desc=current_name):
            self.cen_name = cen_name
            scenario_dict: dict[str, float] = {}
            Directory.SetCurrentDirectory(DWSIMPATH)
            interf = Automation3()
            flowsheet = interf.CreateFlowsheet()

            package_full_name = f'{self.package}PropertyPackage'
            self.instantiated_package = getattr(PropertyPackages, package_full_name)()

            flowsheet.AddPropertyPackage(self.instantiated_package)

            compound_dict = self.get_compound_name(current_value, flowsheet)
            compound_list = self.get_compound_value(current_value, cen_name)

            no_compound_value = all(compound_value == 0 for compound_value in compound_list)
            if no_compound_value:
                continue
                
            temperature_C = current_value[current_value['SCENARIO_Cenário'] == cen_name]['OVERALL_Temperature'].values[0] # C
            temperature_K = temperature_C + 273.15 # K

            pressure_column_name = difflib.get_close_matches('OVERALL_Pressure', current_value.columns, n=1)
            pressure_value = current_value[current_value['SCENARIO_Cenário'] == cen_name][pressure_column_name[0]].values[0]
            pressure_unit = pressure_column_name[0].rsplit('_')[-1]

            pressure_unit_conv = {
                'kgf/cm2': 98.0665,
                'Pa': 1 / 1000,
                'kPa': 1,
                'atm': 101.325
            }

            pressure_kPa = pressure_value * pressure_unit_conv.get(pressure_unit, 1)

            flow_rate_name = current_value.columns[6] # Mass Flow, Molar Flow or Volume Flow
            flow_rate = str(current_value[current_value['SCENARIO_Cenário'] == cen_name][flow_rate_name].values[0]) # kg/h, kmol/h or m3/h

            gas_flow = current_value[current_value['SCENARIO_Cenário'] == cen_name]['OVERALL_Gas_flow'].values[0]
            oil_flow = current_value[current_value['SCENARIO_Cenário'] == cen_name]['OVERALL_Oil_flow'].values[0]
            water_flow = current_value[current_value['SCENARIO_Cenário'] == cen_name]['OVERALL_Water_flow'].values[0]
            liquid_flow = oil_flow + water_flow

            [flowsheet.SelectedCompounds.Add(compound.Key, compound.Value) for compound in compound_dict.values()]
            ms1 = flowsheet.AddObject(ObjectType.MaterialStream, 50, 50, "Current")
            self.mst = ms1.GetAsObject()

            scenario_dict['SCENARIO_Cenário'] = cen_name
            scenario_dict['OVERALL_Temperature'] = temperature_C
            scenario_dict['OVERALL_Pressure'] = pressure_kPa

            # Flash @P&T
            self.flash_operation(compound_list, pressure_value, 
                                 temperature_K, flow_rate_name.lower(), pressure_unit,
                                 flow_rate, gas_flow, liquid_flow, 'Flash @P&T')
            
            scenario_dict = self.get_overall_data(scenario_dict)

            scenario_dict = self.get_pt_flash_data(scenario_dict)

            # Flash @STD
            self.flash_operation(compound_list, '101325', 
                                 '298.15', flow_rate_name.lower(), 'Pa', 
                                 flow_rate, 1, 1, 'Flash @STD')

            scenario_dict = self.get_std_flash_data(scenario_dict, temperature_K)

            new_compound_list = self.get_compound_value_after_flash(compound_dict)

            self.get_all_compound_value(compound_dict)

            self.cen_comp_dict[cen_name] = self.current_comp_dict

            scenario_dict = self.get_compounds_molar_fraction(scenario_dict, new_compound_list, current_value)

            scenario_df = self.get_scenario_dataframe(dataframe_base, scenario_dict)
            
            dataframe_base = pd.concat([dataframe_base, scenario_df], axis=0)
        
        return dataframe_base

    def dwsim_main_flash_operation(self, full_df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        flashed_df_dict: dict[str, pd.DataFrame] = {}
        for current_index, (current_name, current_value) in enumerate(full_df_dict.items()):
            self.cen_comp_dict: dict[str, dict[str, list[float]]] = {}
            custom_logger.log(f'{current_name} ({current_index + 1}/{len(full_df_dict)})')

            current_value = self.replace_compound_names_dataframe(current_value)

            current_database = self.operations_per_scenario(current_name, current_value)

            current_database = current_database.fillna(value=-1)
            current_database.reset_index(inplace=True, drop=True)

            self.composition_dict[current_name] = self.cen_comp_dict
            flashed_df_dict[current_name] = current_database


        return flashed_df_dict
    