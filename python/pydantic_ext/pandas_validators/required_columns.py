from dataclasses import dataclass
from typing import TypeAlias

import pandas as pd

from ..validator_wrappers import PydanticAfterValidator

ColumnName: TypeAlias = str
ColumnType: TypeAlias = str


@dataclass(frozen=True)
class RequiredColumns(PydanticAfterValidator):
    column_map: dict[ColumnName, ColumnType]

    def validate(self, value: pd.DataFrame) -> pd.DataFrame:
        exceptions = []
        value_column_map = {column_name: value[column_name].dtype for column_name in value.columns}
        for column_name, required_dtype in self.column_map.items():
            if column_name not in value_column_map:
                raise ValueError(f"Required column doesn't exist: {column_name}")
                # exceptions.append(RequiredColumnDoesntExistError(column_name))
                # continue
            if required_dtype != "object" and required_dtype != (
                current_dtype := value_column_map[column_name]
            ):
                raise ValueError(
                    f"Required column: {column_name} doesn't have the correct type: {required_dtype}. Current type: {current_dtype}"
                )
                # exceptions.append(
                #     RequiredColumnTypeMismatchError(column_name, required_dtype, current_dtype)
                # )
        if exceptions:
            raise ExceptionGroup("pandas_required_columns", exceptions)
        return value
