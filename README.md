# ds_validator
Pydantic compatible validators for data science (ds) objects.

## Intoduction
This package provides a simple way to add metadata in type hints for data science types.
This provides 2 functions:
- Provides readers/users of the code with additional information about data science types
- Enables optional requirement validation using `pydantic`

Specifying the metadata in this way will slightly impact initialization, but won't otherwise change performance if validation is not used.

Read more about the motivation of the project [below](#motivation).

## Example
The code below sets the metadata for the `Weights` type to require a `torch.int64` data type and a shape of `(2, 2)`.  The typing system still sees `Weights` as `torch.Tensor`.

> In Python 3.12+, use the [`type`](https://docs.python.org/3/reference/simple_stmts.html#the-type-statement) keyword instead of `TypeAlias`.
    ```python
    # <=3.11
    Weights: TypeAlias = torch.Tensor
    # >= 3.12
    type Weights = torch.Tensor
    ```

```python
from typing import Annotated, TypeAlias

from ds_validator.torch import torch_dtype, torch_shape
import torch

Weights: TypeAlias = Annotated[
    torch.Tensor, torch_dtype(data_type=torch.int64), torch_shape(shape=(2, 2))
]

# the typing system checks `good_data` to see if it matches `torch.Tensor`
good_data: Weights = torch.zeros(2, 2, dtype=torch.int64)
bad_data: Weights = torch.zeros(1, 3, dtype=torch.int32)
```

The `Weights` type can be used in-place of the `torch.Tensor` type hint wherever appropriate.
`good_data` and `bad_data` can be used anywhere `torch.Tensor` is used without typing error.

To leverage validation, you use 1 of 3 `pydantic` Objects:
- [`BaseModel`](#class-that-inherits-from-basemodel)
- [`validate_call`](#decorating-a-function-using-validate_call)
- [`TypeAdapter`](#creating-a-typeadapter-object)

`ds_validator` has wrapped these objects to avoid some configuration boilerplate:
- [`ds_validator.DsBaseModel`](#dsbasemodel)
- [`ds_validator.ds_validate_call`](#ds_validate_call)
- [`ds_validator.ds_type_adapter`](#ds_type_adapter)

Below is an example of validation:

```python
from ds_validator import ds_validate_call

# `pydantic` will validate input and return of the function
@ds_validate_call(validate_return=True)
def modify_weights(tensor_1: Weights, tensor_2: Weights) -> Weights: ...

# this will fail because `bad_data` fails the validation requirements
weight_result = add_weights(good_data, bad_data)
```

## Validators Available
> All arguments in validators must be keyword only!

### Numpy
All validators will be used in a fashion similar to the following:

```python
from typing import Annotated, TypeAlias

from ds_validator.numpy import np_dtype, np_shape
import numpy as np

# Array is a placeholder, this name can be anything

# python 3.12+
type Array = Annotated[np.Array, <1 or more np validators>]
# python <=3.11
Array: TypeAlias = Annotated[np.Array, <1 or np validators>]

# example
Array: TypeAlias = Annotated[np.Array, np_dtype(data_type=np.integer), np_shape(shape=("x", "x"))]
```

#### `np_dtype`
Ensures that a `np.ndarray` object adheres to one of the data types specified in the `data_type` kwarg.

The `data_type` kwarg is either a single `nd.dtype` or a set of `nd.dtype`. If a set, the validation will return true if any of the `nd.dtype` in the set match the data data type.

The validator uses `np.issubdtype` to determine if the data type is a subclass of something
in `data_type`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.

#### `np_shape`
Ensures that a `np.ndarray` object adheres to a particular shape specified in `shape` kwarg.

The `shape` kwarg type is described [below](#shape).

### Pandas
There are separate validators for DataFrame (df) and Series objects.

Arrow and Numpy data types are supported in the validators below.

#### DataFrame (df)
All validators will be used in a fashion similar to the following:

```python
from typing import Annotated, TypeAlias

from ds_validator.pandas import (
    df_dtype,
    df_index,
    df_shape,
)
import numpy as np
import pandas as pd
import pyarrow as pa
# DataFrame is a placeholder, this name can be anything

# python 3.12+
type DataFrame = Annotated[pd.Dataframe, <1 or more df validators>]
# python <=3.11
DataFrame: TypeAlias = Annotated[pd.Dataframe, <1 or more df validators>]

# example
DataFrame: TypeAlias = Annotated[
    pd.DataFrame,
    df_dtype(
        column_map={"Name": np.object_, "Quantity": {np.integer, pd.ArrowDType(pa.int64())}},
        other_columns="forbid",
    ),
    np_index(required_indicies={"test", "test_1"}, allow_extra=True),
    df_shape(shape=(None, 4)),
]
```

##### df_dtype
Ensures that `pd.DataFrame` object has the correct column names and types.

The `column_map` kwarg is a dictionary where keys are column names and values are acceptable data types. Acceptable data types are `np.dtype`, `pd.ArrowDType`, or a literal string "any". If the type is "any" the column's type is not checked.  If the value is a set of acceptable types, a match to any type validates the column.

The `other_columns` kwarg deals with any other columns not listed in `column_map`. If it is one of the acceptable types above (or a set of acceptable types), all other colums will be validated against that type.  If the value is a literal "forbid", then columns not included in `column_map` are allowed.

If numpy type, uses `np.issubdtype` to determine if the column's data type is a subclass of something
in the value of `column_map`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
for more information.

Arrow types require an exact match.

##### df_index
Ensures that specific indexes are present in the dataframe.

The `required_indicies` kwarg is a set of indicies that are required to be in the dataframe. Since indexes are hashable, each one must be an exact match.

The `allow_extra` kwarg is a boolean indicating if other indicies are allowed outside of the ones listed in `required_indicies`.

##### df_shape
Ensures that DataFrame adheres to a specific shape.

The `shape` kwarg is a 2-Tuple of the types listed in the [Shape](#shape) section.

#### Series
All validators will be used in a fashion similar to the following:

```python
from typing import Annotated, TypeAlias

from ds_validator.pandas import (
    series_dtype,
    series_index,
    series_name,
    series_shape,
)
import numpy as np
import pandas as pd
import pyarrow as pa
# Series is a placeholder, this name can be anything

# python 3.12+
type Series = Annotated[pd.Series, <1 or more series validators>]
# python <=3.11
Series: TypeAlias = Annotated[pd.Series, <1 or more series validators>]

# example
Series: TypeAlias = Annotated[
    pd.Series,
    series_dtype(data_type={np.integer, pd.ArrowDType(pa.int64())}),
    series_index(required_indicies={"test", "test_1"}, allow_extra=True),
    series_name(name="Quantity"),
    series_shape(shape=(4,)),
]
```

##### series_dtype
Ensures that the Series has the required data type.

The `data_type` kwarg represents an acceptable set of data types: `np.dtype` or `pd.ArrowDType`.  "any" is not a valid argument since that would make the validator pointless. If a set of acceptable types, a match against any type will result in validation.

If numpy type, uses `np.issubdtype` to determine if `value_dtype` is a subclass of something
in `data_type`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.

Arrow types require an exact match.

##### series_index
Ensures that specific indexes are present in the Series.

The `required_indicies` kwarg is a set of indicies that are required to be in the Series. Since indexes are hashable, each one must be an exact match.

The `allow_extra` kwarg is a boolean indicating if other indicies are allowed outside of the ones listed in `required_indicies`.

##### series_name
Ensures that the Series name matches the requirements.

The `name` kwarg is a hashable value that is compared the name of the series. It must be an exact match.

##### series_shape
Ensures the shape of the Series matches the requirements.

The `shape` kwarg is a 1-Tuple of either `int | range`.  All other values in the [Shape](#shape) will always make the validator return `True`.

### Torch
All validators will be used in a fashion similar to the following:

```python
from typing import Annotated, TypeAlias

from ds_validator.torch import (
    tensor_device,
    tensor_dtype,
    tensor_shape,
)
import torch
# Tensor is a placeholder, this name can be anything

# python 3.12+
type Tensor = Annotated[torch.Tensor, <1 or more tensor validators>]
# python <=3.11
Tensor: TypeAlias = Annotated[torch.Tensor, <1 or more tensor validators>]

# example
Tensor: TypeAlias = Annotated[
    torch.Tensor,
    tensor_device(device=torch.device("cuda:1"), match_index=True),
    tensor_dtype(data_type=torch.int64),
    tensor_shape(shape=(None, 3, range(1, 10), "x", "x")),
]
```

#### tensor_device
Ensures the the Tensor is on the correct device.

The `device` kwarg is a `torch.device` type.

The `match_index` kwarg indicates if the index of the `device` kwarg will be matched to the Tensor.
If `match_index=False`, just the device type will be matched. For example, if `device=torch.device("cuda:0")` and `match_index=False` then this will validate if the tensor is on `cuda:0` ... `cuda:N`.
If `match_index=True`, only `cuda:0` will match.

#### tensor_dtype
Ensures that Tensor object meets data type requirements.

The `data_type` kwarg is the acceptable data type(s) of the function: `torch.dtype`. If it is a set, the Tensor can match any of the data types in the set.

#### tensor_shape
Ensures the shape of the Tensor meets requirements.

The `shape` kwarg is described [below](#shape).

### Shape
The `shape` argument is `tuple[int | range | str | None, ...]`.
There is one value in the tuple for each dimension of the shape.
The values provided for each dimension mean the following:
- `int`: A fixed size for this dimension.
- `range`: A range of integers for this dimension (inclusive).
- `str`: Represents a variable. The first instance of the variable can be anything,
but all subsequent dimensions with the same string must match.
- `None`: There are no size limitations for this dimension.

The `shape` tuple below represents a 5-dimensional shape where:
- Dimension 0 is fixed at 3
- Dimension 1 is a range between 1 and 10 (inclusive)
- Dimension 2 and 3 must be the same size
- Dimension 4 can be any size

`shape = (3, range(1, 10), "x", "x", None)`

## Pydantic Adapters
When using `pydantic` with standard data science types, a pydantic configuration: `arbitrary_types_allowed=True` needs to be set.

Furture versions this package may have classes to provide `pydantic` the [information necessary](https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types) so that this configuration isn't nesessary.

However, to help reduce the bolierplate this package includes the following objects.  They all work assuming with the following code:

```python
from typing import Annotated, TypeAlias

from ds_validator.torch import tensor_dtype, tensor_shape
import torch

ENSEMBLE_MODELS = 3
EMBEDDING_COUNT = 34

# common validation criteia have functions that return `AfterValidators`
EnsembleModel: TypeAlias = Annotated[
    torch.Tensor,
    tensor_dtype(data_type=tensor.int64),
    # Dimenions 0 and 2 have an exact required size, Dimenion 1 can be any size
    tensor_shape(shape=(ENSEMBLE_MODELS, None, EMBEDDING_COUNT)),
]

good_data = torch.zeros(3, 15, 34, dtype=torch.int64)
bad_data = torch.zeros(4, 5, 3, dtype=torch.int32)
```

### DsBaseModel
Inherits from [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/concepts/models/). Can be used exactly like `pydantic.BaseModel`:

```python
from ds_validator import DsBaseModel
import torch

class AllModelData(DsBaseModel):
    ensemble_model: EnsembleModel


# good_model will work without error
good_model = AllModelData(ensemble_model=good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = AllModelData(ensemble_model=bad_data)
```

### ds_validate_call
Creates a [`pydantic.validate_call`](https://docs.pydantic.dev/latest/concepts/validation_decorator/) object with the correct configuration for data science types. Can be used exactly like `pydantic.validate_call`

```python
from ds_validator import ds_validate_call
import torch

# without `validate_return=True`, `pydantic` will just validate inputs
@ds_validate_call(validate_return=True)
def transform_ensemble(tensor: EnsembleModel) -> EnsembleModel: ...


# good_model will work without error
good_model = transform_ensemble(tensor=good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = transform_ensemble(bad_data)
```

### ds_type_adapter
Creates a [`pydantic.TypeAdapter`](https://docs.pydantic.dev/latest/concepts/type_adapter/) object that will work with data science types. Has the same arguments as `pydantic.TypeAdapter`.

```python
from ds_validator import ds_type_adapter
import torch

ensemble_adapter = ds_type_adapter(EnsembleModel)

# good_model will work without error
good_model = ensemble_adapter.validate_python(good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = ensemble_adapter.validate_python(bad_data)
```

## Bundling Validators
If multiple Validators are used, the first validator to find an error raises and error and the subsequent validators do not run. If you would like multiple validators to run (for example, to find all object errors during testing), validators can be combined with the `bundle` function:

```python
from typing import Annotated, TypeAlias

from ds_validator import bundle
from ds_validator.torch import (
    tensor_device,
    tensor_dtype,
    tensor_shape,
)
import torch

Tensor: TypeAlias = Annotated[
    torch.Tensor,
    # dtype and shape validators will run even if there is an error in device validator
    bundle(
        tensor_device(device=torch.device("cuda:1"), match_index=True),
        tensor_dtype(data_type=torch.int64),
        tensor_shape(shape=(None, 3, range(1, 10), "x", "x")),
    ),
]
```

## Creating Custom Validators
Additional validators can be created by using instances of pydantic's [`AnnotatedValidators`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).

If you would like to create a validator that behaves in the same way as the validators in the package, create a function with the following signature:

```python
def custom_error_finder(data: <Type to Validate>, *, <0 or more kwargs>) -> list[str]: ...

# Example
def tensor_dimensions_error_finder(data: torch.Tensor, *, dimensions: int) -> list[str]:
    if data.dim != dimensions:
        return [
            f"Tensor doesn't match required dimensions {dimensions}, data dimensions: {data.dim}."
        ]
    return []
```

This is an `error_finder` function.  It takes in the data and arguments and creates a `list[str]` with all the errors found.

Then we use a couple of decorators to create a validator:

```python
from ds_validator import create_after_validator, create_checker

# create a checker function that will raise a `PydanticCustomError` if the error finder
# return is not empty
# The checker function has the same arugments as the error finder function.
# The first argument is the name of the error that will appear in the pydantic error
tensor_dimensions_checker = create_checker(
    "torch_tensor_dimension_error", tensor_dimensions_error_fider
)
# This function will require kwargs for everything besides `data` in the error finder
# function that doesn't have a default
# The return of this function is an instance of `pydantic.AfterValidator`
tensor_dimensions = create_after_validator(tensor_dimensions_checker)
```

`tensor_dimensions` can be used similarly to any included validator above.

## Motivation
Type hints for data science objects are not very descriptive:

```python
import pandas as pd

def get_sale_items(items: pd.DataFrame) -> pd.DataFrame: ...
```

A reader of this function might ask the following questions:
- Do the columns of the input match the output?
- What are the names of the columns?
- What are the data types of the columns?

```python
import torch

def normalize_ensemble(ensemble: torch.Tensor) -> torch.Tensor: ...
def pooler(tensor: torch.Tensor) -> torch.Tensor: ...
def reducer(tensor: torch.Tensor) -> torch.Tensor: ...
```

A reader of this function might ask the following questions:
- What is the shape of these tensors?
- Are all the tensor objects the same?
- What is the data typer of these tensors?

These type hints are a good start, but users have to read comments or understand the code to understand what the actual inputs/outputs are of a function.

There are some ways that we can help improve this:

### Liberal Use of [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias)
> In Python 3.12+, using the [`type`](https://docs.python.org/3/reference/simple_stmts.html#the-type-statement) keyword is the preferred style. The lines below reflect the old and new styles:
    ```python
    # <=3.11
    Weights: TypeAlias = torch.Tensor
    # >= 3.12
    type Weights = torch.Tensor
    ```

`TypeAlias` can help make functions more readable and expressive:

```python
from typing import TypeAlias

import pandas as pd

Items: TypeAlias = pd.DataFrame
"""Columns and types are: {"name": np.object_, "quantity": np.integer, "cost": np.integer, "on_sale": np.bool}."""

def get_sale_items(items: Items) -> Items: ...
```

This can help the reader understand that the input and output should be similar (have the same columns/types), eventhough the types are functionally the same. Adding comments for the `TypeAlias` can also help give the reader additional information.

Here is an improvement on the Torch example above:

```python
from typing import TypeAlias

import torch

ModelEnsemble: TypeAlias = torch.Tensor
"""Has shape of (x, n, m) where: x = models, n = model elements, m = embedding count"""
Model: TypeAlias = torch.Tensor
"""Has shape of (n, m) where: x = models, n = model elements, m = embedding count"""
ElementScore: TypeAlias = torch.Tensor
"""Has shape of (n) where: n = model elements"""

def normalize_ensemble(ensemble: ModelEnsemble) -> Model: ...
def pooler(tensor: Model) -> Model: ...
def reducer(tensor: Model) -> ElementScore: ...
```

This significantly improves readability! These comments can be put in the functions, but if these types are used in multiple functions, it is helpful to have a centralized place to store documentation on the type.

Of course, there are no guarantees at runtime that these shapes are going to be what is expected.
While not always necessary, it would be nice to have the option to validate the data. The next option provides the reader information and can optionally validate data in several ways using `pydantic`.

### Use [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) Type
By adding specific metadata to type hints (specifically [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators)), we can both provide the user with critical information and provide optional validation using `pydantic`:

```python
import functools
from typing import Annotated, TypeAlias

import torch
from pydantic import AfterValidator

def tensor_dtype(data: torch.Tensor, data_type: torch.dtype) -> torch.Tensor:
    if data.dtype != data_type:
        raise ValueError(f"Tensor must have type {data_type}, current type: {data.dtype}.")
    return data

int64_dtype = functools.partial(tensor_dtype, data_type=torch.int64)
# this type informs the user that is should be of type `torch.int64`
EnsembleModel: TypeAlias = Annotated[torch.Tensor, AfterValidator(int64_dtype)]

good_data = torch.zeros(3, 15, 34, dtype=torch.int64)
bad_data = torch.zeros(4, 5, 3, dtype=torch.int32)
```

`EnsembleModel` now has metadata about the data type in the type hint and `pydantic` can use it for validation in multiple ways:

> In all cases below, the `pydantic` configuration option `arbitrary_types_allowed=True` needs to be set for data science objects.  This is because they don't inherit from `BaseModel`, aren't part of the Python standard library, and don't currently have objects that can obtain [`pydantic` schema](https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types).

#### Class that inherits from [`BaseModel`](https://docs.pydantic.dev/latest/concepts/models/)

```python
from pydantic import BaseModel, ConfigDict
import torch

class AllModelData(BaseModel):
    ensemble_model: EnsembleModel

    model_config = ConfigDict(arbitrary_types_allowed=True)


# good_model will work without error
good_model = AllModelData(ensemble_model=good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = AllModelData(ensemble_model=bad_data)
```

#### Decorating a function using [`validate_call`](https://docs.pydantic.dev/latest/concepts/validation_decorator/)

```python
from pydantic import ConfigDict, validate_call
import torch

# without `validate_return=True`, `pydantic` will just validate inputs
@validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
def transform_ensemble(tensor: EnsembleModel) -> EnsembleModel: ...


# good_model will work without error
good_model = transform_ensemble(tensor=good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = transform_ensemble(bad_data)
```

#### Creating a [`TypeAdapter` Object](https://docs.pydantic.dev/latest/concepts/type_adapter/)
Allows for validation of objects anywhere within your code.
Really useful for testing since you can validate objects without changing the performance of your code.

```python
from pydantic import ConfigDict, TypeAdapter
import torch

ensemble_adapter = TypeAdapter(EnsembleModel, config=ConfigDict(arbitrary_types_allowed=True))

# good_model will work without error
good_model = ensemble_adapter.validate_python(good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = ensemble_adapter.validate_python(bad_data)
```

### Use `ds_validator`
Setting up metadata for use in `pydantic` contains some hassles:
- All `pydantic` validation mechanisms require `arbitrary_types_allowed=True`
- To make validation criteria generic, `functools.partial` needs to be used for every variation of criteria

`ds_validator` helps elimiate these hassles and makes new validators easier to create.

```python
from typing import Annotated, TypeAlias


from ds_validator import ds_type_adapter
from ds_validator.torch import tensor_dtype, tensor_shape
import torch

ENSEMBLE_MODELS = 3
EMBEDDING_COUNT = 34

# common validation criteia have functions that return `AfterValidators`
EnsembleModel: TypeAlias = Annotated[
    torch.Tensor,
    tensor_dtype(data_type=tensor.int64),
    # Dimenions 0 and 2 have an exact required size, Dimenion 1 can be any size
    tensor_shape(shape=(ENSEMBLE_MODELS, None, EMBEDDING_COUNT)),
]

# ds_type_adapter has `arbitrary_types_allowed=True` but has
# the same options as `pydantic.TypeAdapter`
ensemble_adapter = ds_type_adapter(EnsembleModel)
# ds_validate_call and DsBaseModel do the same thing for `validate_call` and `BaseModel`

# good_model will work without error
good_model = ensemble_adapter.validate_python(good_data)
# pydantic will raise an error because `bad_data` doesn't match validation requirements
bad_model = ensemble_adapter.validate_python(bad_data)
```