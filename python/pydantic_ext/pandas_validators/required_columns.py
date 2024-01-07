from dataclasses import dataclass
from typing import TypeAlias

import pandas as pd

from pydantic_ext import create_validator_error
from pydantic_ext.validator_wrappers import PydanticAfterValidator

ColumnName: TypeAlias = str
ColumnType: TypeAlias = str


@dataclass(frozen=True, slots=True)
class RequiredColumns(PydanticAfterValidator):
    column_map: dict[ColumnName, ColumnType]

    def validate(self, value: pd.DataFrame) -> pd.DataFrame:
        validation_errors = []
        value_column_map = {column_name: value[column_name].dtype for column_name in value.columns}
        for column_name, required_dtype in self.column_map.items():
            if column_name not in value_column_map:
                validation_errors.append(f"Required column doesn't exist: `{column_name}`")
                continue
            if required_dtype != "object" and required_dtype != (
                current_dtype := value_column_map[column_name]
            ):
                validation_errors.append(
                    f"Required column `{column_name}` of type `{current_dtype}` doesn't have the correct type: `{required_dtype}`"
                )
        if validation_errors:
            raise create_validator_error(
                "pandas_dataframe_required_columns_error", validation_errors
            )
        return value
