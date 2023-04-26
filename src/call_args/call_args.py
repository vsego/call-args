"""
Main class for `call_args`.
"""

import inspect
from typing import TypeVar, Generic, Callable, Any, Iterable


SourceT = TypeVar("SourceT")
ReturnT = TypeVar("ReturnT")


class CallError(Exception):
    """
    Internal exception to capture call errors and modify tracebacks.
    """

    def __init__(self, ex: Exception) -> None:
        self.ex = ex


class CallArgs(Generic[ReturnT]):
    """
    Execute callables by using arguments from a single source.

    :param f: The callable to be called with arguments from `source`.
    :param source: The source of data.
    :param item_getter: A callable taking `source` and a string `name` for
        which it returns the value of that name from the source. In case that
        there is no such item, any exception can be raised.
    :param all_getter: A callable taking `source` and returning an iterable of
        names of all values available in it. Each of the name must represent a
        value that can be fetched with `item_getter`.
    :param kwargs_as_default: This flag defines the role of the extra keyword
        arguments in :py:meth:`__call__` (i.e., in :py:func:`call_args_attr`
        and :py:func:`call_args_dict`). If set to `True`, these arguments are
        treated as default values that can be overridden by the values taken
        from `source`. If set to `False`, the behaviour is the opposite: those
        arguments override the values that come from `source`.
    :param skip_private: If `True`, private arguments (those with names
        starting with underscores `_`) are never assigned values. If `False`,
        private arguments are treated the same as the public ones.
    """

    def __init__(
        self,
        f: Callable[..., ReturnT],
        source: SourceT,
        /, *,
        item_getter: Callable[[SourceT, str], Any],
        all_getter: Callable[[SourceT], Iterable[str]],
        kwargs_as_default: bool = False,
        skip_private: bool = True,
    ) -> None:
        self.f = f
        self.source = source
        self.item_getter = item_getter
        self.all_getter = all_getter
        self.kwargs_as_default = kwargs_as_default
        self.skip_private = skip_private

    def get_all_kwargs(self) -> dict[str, Any]:
        """
        Return all keyword arguments from `source` as a dictionary.
        """
        return {
            name: self.item_getter(self.source, name)
            for name in self.all_getter(self.source)
            if not name.startswith("_")
        }

    def get_kwargs(self) -> dict[str, Any]:
        """
        Return keyword arguments for `f` from `source` as a dictionary.
        """
        result: dict[str, Any] = dict()
        for param in inspect.signature(self.f).parameters.values():
            if self.skip_private and param.name.startswith("_"):
                continue
            if param.kind == param.VAR_KEYWORD:
                return self.get_all_kwargs()
            if param.kind in {param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY}:
                try:
                    value = self.item_getter(self.source, param.name)
                except Exception:
                    pass
                else:
                    result[param.name] = value
        return result

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnT:
        """
        Execute the call and return whatever `self.f` returns.
        """
        if self.kwargs_as_default:
            kwargs.update(self.get_kwargs())
        else:
            kwargs = {**self.get_kwargs(), **kwargs}
        try:
            return self.f(*args, **kwargs)
        except Exception as ex:
            raise CallError(ex)
