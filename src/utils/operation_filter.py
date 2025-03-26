from abc import ABC, abstractmethod
from typing import TypeVar
import os
import sqlite3

import pandas as pd
from safeloader import Loader

from enums.filter_operations import OperationsFilter, PhaseType

class Filter(ABC):
    @abstractmethod
    def __init__(self, 
                 filter_type: OperationsFilter,
                 flashed_df_dict: dict[str, pd.DataFrame], 
                 full_info_dict: dict[str, pd.DataFrame],
                 composition_dict: dict[str, dict[str, list[float]]],
                 phase_type: PhaseType,
                 use_simulated_value: bool) -> None:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_filename = 'heat_of_combustion.db'
        self.database_path = os.path.join(base_path, 'files', 'database', db_filename)

        conn = sqlite3.connect(self.database_path)
        query = "SELECT * FROM table_name;"
        self.enthalpy_db = pd.read_sql(query, conn)
        conn.close()

        self.filter_type = filter_type
        self.flashed_df_dict = flashed_df_dict
        self.full_info_dict = full_info_dict
        self.composition_dict = composition_dict
        self.use_simulated_value = use_simulated_value
        self.filtered_data_dict: dict[str, pd.DataFrame] = {}
        self.phase_type = phase_type

        self.operation_loader = Loader(desc=f'Applying operation filter - {self.filter_type.name}', end='done').start()

        self.match_dicts()

        if not self.use_simulated_value:
            self.attribute_infoed_to_simulated()

    
    def match_dicts(self) -> None:
        for key, value in self.flashed_df_dict.items():
            filtered_value = self.full_info_dict[key][self.full_info_dict[key]['SCENARIO_Cenário'].isin(value['SCENARIO_Cenário'].values)]
            filtered_value.reset_index(inplace=True, drop=True)
            self.full_info_dict[key] = filtered_value

    def attribute_infoed_to_simulated(self) -> None:
        current_keys = [k for k in self.flashed_df_dict.keys()]
        for current_key in current_keys:
            self.full_info_dict[current_key].columns = [f'{col}_new' for col in self.full_info_dict[current_key].columns]

            merged_df = pd.concat([self.flashed_df_dict[current_key], self.full_info_dict[current_key]], axis=1)

            for column in self.flashed_df_dict[current_key].columns[1:]:
                if column + '_new' in merged_df.columns:

                    merged_df[column] = merged_df.apply(
                        lambda row: row[column + '_new'] if row[column + '_new'] not in ['-', None] and not pd.isna(row[column + '_new']) else row[column], 
                        axis=1
                    )

            merged_df.drop(columns=[col for col in merged_df.columns if '_new' in col], inplace=True)

            self.flashed_df_dict[current_key] = merged_df

class CalorificValue(Filter):
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
        
        self.calculate_calorific_value()
        for current_filtered_value in self.filtered_data_dict.values():
            current_filtered_value.columns = [column.split('_')[1].strip() if '_' in column else column for column in current_filtered_value.columns]
        self.operation_loader.stop()

    @staticmethod
    def attribute_calorific_value(row: pd.Series, composition_names: list[str], composition_dict, 
                                  phase_type: PhaseType, current_name: str, enthalpy_db: pd.DataFrame) -> str:
        if row['SCENARIO_Cenário'] == 'SCENARIO':
            return 'CALORIFIC'
        
        calorific = 0
        for comp_value, comp_name in zip(composition_dict[current_name][row['SCENARIO_Cenário']][phase_type.value], composition_names):
            if comp_name in enthalpy_db['Composition'].values and comp_value:
                matching_rows = enthalpy_db[enthalpy_db['Composition'] == comp_name]['Enthalpy'].values
                enthalpy_combustion = matching_rows[0] if matching_rows else 0
                calorific += enthalpy_combustion * comp_value # sum (kJ/kmol * frac mol)

        state_conv = {'Overall': 'OVERALL_Molar Flow',
                      'Vapor': 'VAPOUR PHASE_Molar Flow @Std Cond',
                      'Liquid1': 'OILY PHASE_Molar Flow @Std Cond',
                      'Liquid2': 'LIQUID PHASE_Molar Flow @Std Cond'}
        
        molar_flow = row[state_conv[phase_type.value]] # kmol/h
        final_calorific = calorific * molar_flow if molar_flow else 0 # kJ/kmol * kmol/h = kJ/h
        return final_calorific
        
    def get_calorific_value(self, current_database: pd.DataFrame, current_name: str, ph_type: PhaseType) -> pd.DataFrame:
        composition_names = current_database.columns[current_database.iloc[0] == 'COMPONENT FRACTION']
        current_database['Calorific'] = current_database.apply(
            lambda row: self.attribute_calorific_value(
                row, composition_names, self.composition_dict, ph_type, current_name, self.enthalpy_db
            ),
            axis=1
        )
        return current_database

    def calculate_calorific_value(self) -> None:
        for current_name, current_database in self.flashed_df_dict.items():
            if current_database.iloc[1:].empty:
                continue

            current_database = self.get_calorific_value(current_database, current_name, self.phase_type)
            current_database = current_database.fillna(0)

            first_row = current_database.iloc[0]
            current_database = current_database.iloc[1:, :].reset_index(drop=True)

            current_database['Calorific'] = current_database['Calorific'].astype(float)

            max_calorific_row = current_database.iloc[current_database['Calorific'].idxmin()]

            result_df = pd.concat([first_row, max_calorific_row], axis=1).T
            result_df = result_df.iloc[:, :-1]
            result_df = result_df.reset_index(drop=True)

            self.filtered_data_dict[current_name] = result_df

class CO2AndH2SFraction(Filter):
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
        
        self.calculate_CO2_and_H2S()
        for current_filtered_value in self.filtered_data_dict.values():
            current_filtered_value.columns = [column.split('_')[1].strip() if '_' in column else column for column in current_filtered_value.columns]
        self.operation_loader.stop()
        
    def calculate_CO2_and_H2S(self):
        co2_position = list(self.flashed_df_dict.values())[0].columns.str.lower().get_loc('carbon dioxide'.lower())
        h2s_position = list(self.flashed_df_dict.values())[0].columns.str.lower().get_loc('hydrogen sulfide'.lower())
        df = list(self.flashed_df_dict.values())[0]
        index_to_subtract = df.columns.get_loc(df.iloc[0][df.iloc[0] == 'COMPONENT FRACTION'].index[0])
    
        state_conv = {'Overall': 'OVERALL_Molecular Weight @T&P Cond',
                      'Vapor': 'VAPOUR PHASE_Molecular Weight @T&P Cond',
                      'Liquid1': 'OILY PHASE_Molecular Weight @T&P Cond',
                      'Liquid2': 'LIQUID PHASE_Molecular Weight @T&P Cond'}
        
        molecular_weight_position = list(self.flashed_df_dict.values())[0].columns.get_loc(state_conv[self.phase_type.value])
        
        max_co2_or_h2s = {}
        for current_name, current_database in self.composition_dict.items():
            all_co2 = {}
            all_h2s = {}

            for scenario_name, scenario_current_database in current_database.items():
                matched_row = self.flashed_df_dict[current_name].loc[self.flashed_df_dict[current_name]['SCENARIO_Cenário'] == scenario_name]
                co2_val = scenario_current_database[self.phase_type.value][co2_position - index_to_subtract]
                h2s_val = scenario_current_database[self.phase_type.value][h2s_position - index_to_subtract]
                mol_weight_val = matched_row.iloc[0, molecular_weight_position]

                all_co2[scenario_name] = (co2_val, mol_weight_val if mol_weight_val != -1 else 0)
                all_h2s[scenario_name] = (h2s_val, mol_weight_val if mol_weight_val != -1 else 0)

            if not all_co2 or not all_h2s:
                continue
            
            max_value_co2 = max([item[0] for item in all_co2.values()])
            max_value_co2 = next(item for item in all_co2.values() if item[0] == max_value_co2)

            max_value_h2s = max([item[0] for item in all_h2s.values()])
            max_value_h2s = next(item for item in all_h2s.values() if item[0] == max_value_h2s)

            if not max_value_co2[1] and not max_value_h2s[1]:
                continue

            if max_value_co2[0] >= max_value_h2s[0] and ((abs(max_value_co2[1] - max_value_h2s[1]) / ((max_value_co2[1] + max_value_h2s[1]) / 2)) * 100) <= 10:
                for k, v in all_co2.items():
                    if v == max_value_co2:
                        max_co2_or_h2s[current_name + '_CO2_H2S'] = (k, max_value_h2s[0], h2s_position)
            elif max_value_co2[0] < max_value_h2s[0] and ((abs(max_value_co2[1] - max_value_h2s[1]) / ((max_value_co2[1] + max_value_h2s[1]) / 2)) * 100) <= 10:
                for k, v in all_h2s.items():
                    if v == max_value_h2s:
                        max_co2_or_h2s[current_name + '_CO2_H2S'] = (k, max_value_co2[0], co2_position)
            else:
                for k, v in all_co2.items():
                    if v == max_value_co2:
                        max_co2_or_h2s[current_name + '_CO2'] = (k, max_value_co2[0], co2_position)
                for k2, v2 in all_h2s.items():
                    if v2 == max_value_h2s:
                        max_co2_or_h2s[current_name + '_H2S'] = (k2, max_value_h2s[0], h2s_position)

            key_names = []
            for key in max_co2_or_h2s.keys():
                if current_name in key:
                    key_names.append(key)
            
            first_row = self.flashed_df_dict[current_name].loc[[0]]
            for key_name in key_names:
                match_row = self.flashed_df_dict[current_name].loc[self.flashed_df_dict[current_name]['SCENARIO_Cenário'] == max_co2_or_h2s[key_name][0]]
                result = pd.concat([first_row, match_row])
                result.iloc[1, max_co2_or_h2s[key_name][-1]] = max_co2_or_h2s[key_name][1]
                result = result.reset_index(drop=True)
                
                self.filtered_data_dict[key_name] = result

class Dispersion(Filter):
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
        
        self.operation_loader.stop()
        raise NotImplementedError('Dispersion filter not implemented!')

class FilterFactory:
    T = TypeVar('T', bound=Filter)

    filter_classes: dict[OperationsFilter, type[Filter]] = {
        OperationsFilter.CALORIFIC_VALUE: CalorificValue,
        OperationsFilter.CO2_AND_H2S_FRACTION: CO2AndH2SFraction,
        OperationsFilter.DISPERSION: Dispersion
    }

    @staticmethod
    def create_filter(filter_type: OperationsFilter,
                      flashed_df_dict: dict[str, pd.DataFrame],
                      full_info_dict: dict[str, pd.DataFrame],
                      composition_dict: dict[str, dict[str, list[float]]],
                      *, phase_type: PhaseType,
                      use_simulated_value: bool) -> T:
        filter_class = FilterFactory.filter_classes.get(filter_type, OperationsFilter)
        return filter_class(filter_type, flashed_df_dict, full_info_dict, 
                            composition_dict, phase_type, use_simulated_value)
    