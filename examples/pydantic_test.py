from pydantic import validate_call


@validate_call(validate_return=True)
def func_test(a: int, b: bool) -> float:
    return False


func_test(a=2.1, b="test")
