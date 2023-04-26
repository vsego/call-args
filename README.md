# CallArgs

Call functions and create objects by easily assigning values of keyword arguments from some object's attributes of or items from some dictionary.

## Content

1. [Usage](#usage)
2. [Variable keyword arguments](#variable-keyword-arguments)
3. [Extra arguments](#extra-arguments)
4. [Extending the package's functionality](#extending-the-packages-functionality)

## Usage

When calling a function `f` with keyword arguments contained in a dictionary `d`, one can do something like this:

```python
result = f(a=d["a"], b=d["b"],...)
```

or simply unpack `d`:

```python
result = f(**d)
```

Similarly, using attributes of object `obj`, one can do

```python
result = f(a=obj.a, b=obj.b,...)
```

or simply unpack d:

```python
result = f(**vars(d))
```

In both of these cases, the first approach can get tedious if there are many arguments and/or when adding new ones, while the second approach is problematic if a dictionary/object has some items/attributes that `f` does not accept (which is almost always the case with objects' attributes).

Instead, the above calls can be done like this:

```python
from call_args import call_args_dict
result = call_args_dict(f, d)
```

or

```python
from call_args import call_args_attr
result = call_args_attr(f, obj)
```

This can be useful in cases when a dictionary or an object exists specifically for the use with the given callable. For example, when using with command-line arguments:

```python
parser = argparse.ArgumentParser(
    prog=splitext(basename(sys.argv[0]))[0],
    description=sys.modules[__name__].__doc__,
)
...
args = parser.parse_args()
call_args_attr(ClassThatDoesTheJob, args).run()
```

The `call_args_*` functions filter out the values that `f` would not understand, as well as all the private ones (those with names starting with underscore `_`).

## Variable keyword arguments

If the callable allows variable keyword arguments, then the whole source will be used. This means that

```python
def f(**kwargs):
    ...

result1 = call_args_dict(f, d)
result2 = call_args_attr(f, obj)
```

is _mostly_ equivalent to

```python
def f(**kwargs):
    ...

result1 = f(**d)
result2 = f(**vars(obj))
```

However, there is still a difference: even in this case, `call_args_*` functions will not assign values to private arguments, which means that all the items from `d` and attributes from `obj` with names starting with an underscore `_` will be omitted.

Also, in the case of an object - which might have methods - filtering of names is still useful, as those won't be unpacked (unless the callable expects attributes with exactly those names).

## Extra arguments

The calls presented above can accept extra arguments. For example,

```python
def f(a=17, b=19, c=23):
    print(a, b, c)

data = {"b": "29", "c": 31, "d": 37}
call_args_dict(f, data, c=41)
```

will print `17 29 41` because:

* `a` is not defined in `data` nor among keyword arguments of `call_args_dict`, so it retains its default value;

* `b` is defined only in `data`, getting its value 29 from there;

* `c` is defined in `data`, but also in keyword arguments of `call_args_dict`, which are prioritised and thus provide the value 41;

* `d` is defined in `data`, but it is not accepted by `f`, so `call_args_dict` silently drops it.

Note that explicitly given keyword arguments are always passed to `f`. This call:

```python
call_args_dict(f, {"b": "29", "c": 31, "d": 37}, c=41, e=43)
```

raises a `TypeError` exception with a message

```
TypeError: f() got an unexpected keyword argument 'e'
```

## Extending the package's functionality

The work here is done by the class `CallArgs`. Other "classes" (`CallArgsAttr` specifically for working with attributes and `CallArgsDict` for working with dictionaries) are dynamically generated, and they are not classes at all. They are `partial` objects.

The two functions used above are also dynamically generated.

So, in order to modify or extend the functionality presented above, one only needs to inherit `CallArgs`, and then recreate these two partials and two functions.

Let us assume that we have a new class `NewCallArgs`, inherited from `CallArgs`. These interfaces are created with one of the following calls:

```python
# All four together:
CallArgsAttr, CallArgsDict, call_args_attr, call_args_dict = build_interfaces(
    NewCallArgs,
)
# Only "classes" (partials):
CallArgsAttr, CallArgsDict = build_classes(NewCallArgs)
)
# Only functions:
call_args_attr, call_args_dict = build_functions(NewCallArgs)
```

The `build_*` functions accept extra keyword arguments that are passed on to
the class constructor, in order to easily modify the default behaviour.
Currently, there are two such arguments:

```python
call_args_attr2, call_args_dict2 = build_functions(
    CallArgs, kwargs_as_default=True, skip_private=False,
)
```

Setting `skip_private` to `False` means that the functions will no longer filter out such attributes.

Seeting `kwargs_as_default` to `True` changes the meaning of keyword arguments in the newly created functions, so that they are treated as default values instead of overrides of the data. Let us reuse one of the above examples:

```python
def f(a=17, b=19, c=23):
    print(a, b, c)

data = {"b": "29", "c": 31, "d": 37}

# Default behaviour described above:
call_args_dict(f, data, c=41)
# 17 29 41

# Modified behaviour where `c=41` serves as a default value:
call_args_dict2(f, data, c=41)
# 17 29 31  -> 31 comes from `data`
data.pop("c")
call_args_dict2(f, data, c=41)
# 17 29 41
```
