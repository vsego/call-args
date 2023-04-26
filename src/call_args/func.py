"""
Functions that make `CallArgs` easy to use.
"""

from functools import partial
import operator
from typing import TypeVar, TypeAlias, Callable, Any

from .call_args import CallArgs, SourceT, CallError


ReturnT = TypeVar("ReturnT")
CallArgsT: TypeAlias = Callable[[Callable[..., ReturnT], SourceT], ReturnT]


def build_classes(
    base_class: type[CallArgs], **kwargs: Any,
) -> tuple[partial[CallArgs], partial[CallArgs]]:
    """
    Return a 2-tuple of partials for using `call_args`.
    """
    return (
        partial(
            base_class,
            item_getter=getattr,
            all_getter=dir,
            **kwargs,
        ),
        partial(
            base_class,
            item_getter=operator.getitem,
            all_getter=iter, **kwargs,
        ),
    )


def _build_functions(
    class_attrs: partial[CallArgs], class_dict: partial[CallArgs],
) -> tuple[CallArgsT, CallArgsT]:
    """
    Return a 2-tuple of functions for using `call_args`.
    """
    def call_args_attr(
        f: Callable[..., ReturnT],
        source: Any,
        *args: Any,
        **kwargs: Any,
    ) -> ReturnT:
        """
        Call `f` with arguments from an object `source`.

        :param f: A callable to call.
        :param source: An object whose attributes are used to feed the
            arguments of `f`.
        :param args: Extra positional arguments for `f`.
        :param kwargs: Extra keyword arguments to be used, either as defaults
            or as overrides of the data from `source`.
        :return: Whatever `f(...)` returns when called with `*args` and a
            combination of data from `source` and `kwargs`.
        """
        try:
            return class_attrs(f, source)(*args, **kwargs)
        except CallError as ex:
            ex.ex.__suppress_context__ = True
            ex.ex.__traceback__ = None
            raise ex.ex

    def call_args_dict(
        f: Callable[..., ReturnT],
        source: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> ReturnT:
        """
        Call `f` with arguments from a dictionary `source`.

        :param f: A callable to call.
        :param source: A dictionary whose items are used to feed the arguments
            of `f`.
        :param args: Extra positional arguments for `f`.
        :param kwargs: Extra keyword arguments to be used, either as defaults
            or as overrides of the data from `source`.
        :return: Whatever `f(...)` returns when called with `*args` and a
            combination of data from `source` and `kwargs`.
        """
        try:
            return class_dict(f, source)(*args, **kwargs)
        except CallError as ex:
            ex.ex.__suppress_context__ = True
            ex.ex.__traceback__ = None
            raise ex.ex

    return call_args_attr, call_args_dict


def build_functions(
    base_class: type[CallArgs], **kwargs: Any,
) -> tuple[CallArgsT, CallArgsT]:
    """
    Return a 2-tuple of functions for using `call_args`.
    """
    return _build_functions(*build_classes(base_class, **kwargs))


def build_interfaces(
    base_class: type[CallArgs], **kwargs: Any,
) -> tuple[partial[CallArgs], partial[CallArgs], CallArgsT, CallArgsT]:
    """
    Return a 4-tuple of classes and functions for using `call_args`.
    """
    classes = build_classes(base_class, **kwargs)
    return (*classes, *_build_functions(*classes))


CallArgsAttr, CallArgsDict, call_args_attr, call_args_dict = build_interfaces(
    CallArgs,
)
