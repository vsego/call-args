import operator
from typing import Any

from call_args import (
    CallArgs, build_functions, build_interfaces, call_args_attr,
    call_args_dict,
)

from .utils import TestsBase


class TestCallArgs(TestsBase):

    def test_bulding(self):
        class CallArgsSubclass(CallArgs):
            def get_kwargs(self) -> dict[str, Any]:
                return {
                    key: 2 * value
                    for key, value in super().get_kwargs().items()
                }

        def wally(x, foo):
            return (x, foo)

        class obj:
            x = 17
            foo = 19

        d = {"x": 17, "foo": 19}

        result_bf = build_functions(CallArgsSubclass)
        result_bi = build_interfaces(CallArgsSubclass)

        self.assertEqual(len(result_bf), 2)
        self.assertEqual(len(result_bi), 4)

        self.assertTrue(result_bi[0].func is CallArgsSubclass)
        self.assertTrue(result_bi[1].func is CallArgsSubclass)

        self.assertEqual(result_bi[0].args, tuple())
        self.assertEqual(
            result_bi[0].keywords,
            {"item_getter": getattr, "all_getter": dir},
        )
        self.assertEqual(result_bi[1].args, tuple())
        self.assertEqual(
            result_bi[1].keywords,
            {"item_getter": operator.getitem, "all_getter": iter},
        )

        r = result_bf[0](wally, obj)
        self.assertEqual(r, (34, 38))

        r = result_bf[1](wally, d)
        self.assertEqual(r, (34, 38))

        r = result_bi[2](wally, obj)
        self.assertEqual(r, (34, 38))

        r = result_bi[3](wally, d)
        self.assertEqual(r, (34, 38))

    def test_arguments(self):
        def wally(x, foo):
            return (x, foo)

        class obj:
            x = 17

        d = {"x": 17}

        self.assertEqual(call_args_attr(wally, obj, foo=13), (17, 13))
        self.assertEqual(call_args_dict(wally, d, foo=13), (17, 13))

    def test_kwargs_defaultness(self):
        def wally(x, foo):
            return (x, foo)

        class obj:
            foo = 17

        d = {"foo": 17}

        call_args_attr_def, call_args_dict_def = build_functions(
            CallArgs, kwargs_as_default=True,
        )

        self.assertEqual(call_args_attr(wally, obj, x=7, foo=13), (7, 13))
        self.assertEqual(call_args_dict(wally, d, x=7, foo=13), (7, 13))

        self.assertEqual(call_args_attr_def(wally, obj, x=7, foo=13), (7, 17))
        self.assertEqual(call_args_dict_def(wally, d, x=7, foo=13), (7, 17))

    def test_private(self):
        def wally(_a=17, b=19):
            return (_a, b)

        def wally_kw(**kwargs):
            return repr(kwargs)

        class obj:
            _a = 71
            b = 91

        d = {"_a": 71, "b": 91}

        self.assertEqual(call_args_attr(wally, obj), (17, 91))
        self.assertEqual(call_args_dict(wally, d), (17, 91))

        self.assertEqual(call_args_attr(wally_kw, obj), "{'b': 91}")
        self.assertEqual(call_args_dict(wally_kw, d), "{'b': 91}")

    def test_extra_kwargs(self):
        def wally(a=17):
            return a

        class obj:
            a = 71

        d = {"a": 71}

        with self.assertRaises(TypeError):
            call_args_attr(wally, obj, b=17)

        with self.assertRaises(TypeError):
            call_args_dict(wally, d, b=17)

        with self.assertRaises(TypeError):
            call_args_attr(wally, obj, a=13, b=17)

        with self.assertRaises(TypeError):
            call_args_dict(wally, d, a=13, b=17)

        self.assertEqual(call_args_attr(wally, obj, a=13), 13)
        self.assertEqual(call_args_dict(wally, d, a=13), 13)
