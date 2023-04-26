from dataclasses import dataclass

from call_args import CallArgsAttr, CallArgsDict

from .utils import TestsBase


# Why are the functions used in tests called "wally"? Well, as any Dilbert
# reader will tell you, it feels like an appropriate name for functions that do
# nothing. :-)

class TestCallArgs(TestsBase):

    def test_get_kwargs_object(self):
        @dataclass
        class Source:
            a: int = 17
            b: str = "foo"
            c: tuple[int, int] = (11, 13)

        def wally(a, b=19, d=23):
            pass

        self.assertEqual(
            CallArgsAttr(wally, Source()).get_kwargs(),
            {"a": 17, "b": "foo"},
        )

    def test_get_kwargs_dict(self):
        def wally(a, b=19, d=23):
            pass

        source = dict(a=17, b="foo", c=(11, 13))
        self.assertEqual(
            CallArgsDict(wally, source).get_kwargs(),
            {"a": 17, "b": "foo"},
        )

    def test_get_var_kwargs(self):
        def wally(a, b=19, d=23, **kwargs):
            pass

        source = dict(a=17, b="foo", c=(11, 13), e={"x": "y"})
        result = CallArgsDict(wally, source).get_kwargs()
        self.assertEqual(result, source)
        self.assertFalse(result is source)

        expected = dict(source)
        source["_should_be"] = "ignored"
        result = CallArgsDict(wally, source).get_kwargs()
        self.assertEqual(result, expected)
