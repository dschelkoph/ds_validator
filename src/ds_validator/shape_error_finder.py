"""Common error finder for data science objects."""

from typing import Annotated, TypeAlias

from pydantic import AfterValidator, Field

from .pydantic_adapters import ds_validate_call


def ensure_positive_range(length_range: range) -> range:
    if length_range.start < 1 or length_range.stop < 1:
        raise ValueError(  # noqa: TRY003
            f"Both start ({length_range.start}) and stop ({length_range.stop}) values "
            "of the range must be postive."
        )
    return length_range


PositiveRange: TypeAlias = Annotated[range, AfterValidator(ensure_positive_range)]
PositiveInt: TypeAlias = Annotated[int, Field(gt=0)]
DimensionValidation: TypeAlias = PositiveInt | PositiveRange | str | None
ShapeValidation: TypeAlias = tuple[DimensionValidation, ...]


# ds_validate_call doesn't currently work
# https://github.com/pydantic/pydantic/issues/7796
@ds_validate_call()
def shape_error_finder(data_shape: tuple[int, ...], shape: ShapeValidation) -> list[str]:
    validation_errors = []

    if len(shape) != len(data_shape):
        validation_errors.append(
            f"Object dimensions ({len(data_shape)}) does not match required dimensions: "
            f"{len(shape)}."
        )

    variable_store: dict[str, int] = {}
    for dim, (data_size, validation_size) in enumerate(zip(data_shape, shape, strict=False)):
        if not validation_size:
            continue
        if isinstance(validation_size, range):
            if data_size not in validation_size:
                validation_errors.append(
                    f"Dimension {dim} size is not in required range: "
                    f"{validation_size.start}-{validation_size.stop}."
                )
            continue
        if isinstance(validation_size, int):
            if data_size != validation_size:
                validation_errors.append(
                    f"Dimension {dim} size ({data_size}) does not equal "
                    f"required length: {validation_size}."
                )
            continue
        if not (variable := variable_store.get(validation_size)):
            variable_store[validation_size] = data_size
            continue
        if variable != data_size:
            validation_errors.append(
                f"Dimension {dim} size ({data_size}) does not match "
                f"set variable: '{validation_size}' = {variable}."
            )

    return validation_errors
