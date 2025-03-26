from abc import ABC, abstractmethod
from typing import TypeVar
import re

from safeloader import Loader
import numpy as np
import pandas as pd

from enums.format_type import FormatType

class Format(ABC):
    @abstractmethod
    def __init__(self, format_type: FormatType, data_dict: str) -> None:
        self.data_dict = pd.read_excel(data_dict, sheet_name=None)
        self.format_type = format_type
        self.all_df_dict: dict[str, pd.DataFrame] = {}
        self.full_info_dict: dict[str, pd.DataFrame] = {}
        self.format_loader = Loader(desc=f'Worksheet formating - {self.format_type.value}', end='done').start()

    def formated_data(self) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
        self.format_loader.stop()
        return self.all_df_dict, self.full_info_dict
    
class FormatDefault(Format):
    def __init__(self, format_type: FormatType, data_dict: str) -> None:
        super().__init__(format_type, data_dict)
        self._format_dicts()

    def _format_dicts(self) -> None:
        for stream_name, stream_value in self.data_dict.items():
            columns = stream_value.columns
            new_columns = [f'SCENARIO_{columns[0]}'] + [f'OVERALL_{col}' if 0 < index <= 6 else col for index, col in enumerate(columns)][1:]
            stream_value.columns = new_columns

            stream_value.columns = [
                col if len(col.split()) != 2 else f"{col.split()[0]} {col.split()[1].lower()}"
                for col in stream_value.columns
            ]

            self.all_df_dict[stream_name] = stream_value

            full_info_df = pd.DataFrame(columns=stream_value.columns[:7])
            full_info_df.loc[0, :] = [col.split('_')[0] for col in stream_value.columns[:7]]
            full_info_df = pd.concat([full_info_df, stream_value.iloc[:, :7]], axis=0)
            full_info_df.reset_index(inplace=True, drop=True)
            self.full_info_dict[stream_name] = full_info_df

class FormatFactory:
    T = TypeVar('T', bound=Format)

    format_classes: dict[FormatType, type[Format]] = {
        FormatType.DEFAULT: FormatDefault
    }

    @staticmethod
    def create_format(format_type: FormatType, data_dict: str) -> T:
        format_class = FormatFactory.format_classes.get(format_type, FormatDefault)
        return format_class(format_type, data_dict)
    