from typing import Annotated, TypeAlias

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ds_validator import DsBaseModel, ds_type_adapter, ds_validate_call
from ds_validator.pandas import df_dtype_validator

NameDf: TypeAlias = Annotated[pd.DataFrame, df_dtype_validator(column_map={"name": np.object_})]


def df_func(data_frame: NameDf) -> bool: ...


@pytest.fixture()
def valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame({"name": ["name_1", "name_2"]})


@pytest.fixture()
def invalid_dataframe() -> pd.DataFrame:
    return pd.DataFrame({"numbers": [1, 2]})


def test_ds_base_model(valid_dataframe):
    class ArbitraryType(DsBaseModel):
        data_frame: pd.DataFrame

    ArbitraryType(data_frame=valid_dataframe)


def test_ds_validate_call_with_func_arg(valid_dataframe, invalid_dataframe):
    df_func_validated = ds_validate_call(df_func)
    df_func_validated(valid_dataframe)

    with pytest.raises(ValidationError):
        df_func_validated(invalid_dataframe)


def test_valide_ds_call_without_func_arg(valid_dataframe, invalid_dataframe):
    df_func_validated = ds_validate_call()(df_func)
    df_func_validated(valid_dataframe)

    with pytest.raises(ValidationError):
        df_func_validated(invalid_dataframe)


def test_ds_type_adapeter(valid_dataframe, invalid_dataframe):
    name_df_validator = ds_type_adapter(NameDf)
    name_df_validator.validate_python(valid_dataframe)

    with pytest.raises(ValidationError):
        name_df_validator.validate_python(invalid_dataframe)
