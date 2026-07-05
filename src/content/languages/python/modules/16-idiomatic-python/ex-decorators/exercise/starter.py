import functools
import logging

log = logging.getLogger(__name__)


def log_calls(func):
    """Decorator: log each call as 'func_name(args) -> result' at INFO level."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: call func, log the call and result, return the result
        result = func(*args, **kwargs)
        return result
    return wrapper


def repeat(times: int):
    """Decorator factory: call the decorated function 'times' times."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: call func 'times' times and return the last result
            result = None
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    @log_calls
    def add(a, b):
        """Add two numbers."""
        return a + b

    add(2, 3)
    print(add.__name__, "|", add.__doc__)

    @repeat(times=3)
    def greet(name):
        print(f"Hello, {name}!")
        return name

    result = greet("world")
    print("last result:", result)
