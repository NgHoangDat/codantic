import inspect
from functools import lru_cache, wraps
from inspect import Signature
from types import FunctionType
from typing import *

from typer import Typer
from typer.models import ArgumentInfo, OptionInfo

__all__ = ["app", "Command", "App"]


class Command:
    pass


class App(Typer):
    @wraps(Typer.command)
    def command(self, *args, callback: Callable = None, **kwargs):
        base = super()

        def decorator(func: Callable):
            __func = func
            if callback is not None:

                @wraps(func)
                def __func(*args, **kwargs):
                    return callback(func(*args, **kwargs))

            base.command(*args, **kwargs)(__func)
            func = FunctionType(
                func.__code__,
                func.__globals__,
                func.__name__,
                func.__defaults__,
                func.__closure__,
            )
            signature = inspect.signature(func)
            parameters = list(signature.parameters.values())
            defaults = []

            for i, parameter in enumerate(parameters):
                if type(parameter.default) == ArgumentInfo:
                    parameter = parameter.replace(default=inspect._empty)
                    parameters[i] = parameter

                if type(parameter.default) == OptionInfo:
                    parameter = parameter.replace(default=parameter.default.default)
                    parameters[i] = parameter

                if parameter.default != inspect._empty:
                    defaults.append(parameter.default)

            setattr(
                func,
                "__signature__",
                Signature(
                    parameters=parameters, return_annotation=signature.return_annotation
                ),
            )
            func.__defaults__ = tuple(defaults)

            class ConcreteCommand(Command):
                @wraps(func)
                def __call__(self, *args: Any, **kwds: Any):
                    return func(*args, **kwds)

            return ConcreteCommand()

        return decorator

    @lru_cache(maxsize=None)
    def sub_app(self, name: str):
        sub_app = App(pretty_exceptions_show_locals=False)
        self.add_typer(sub_app, name=name)
        return sub_app


app = App(pretty_exceptions_show_locals=False)


@app.command()
def about():
    import random

    import cowsay

    char = random.choice(cowsay.char_names)
    print(cowsay.get_output_string(char, "This is a module for managing coco dataset"))
