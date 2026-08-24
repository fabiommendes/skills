---
name: python-functions
description: Style and good practices for Python functions and methods (implementing and refactoring)
---

# python-functions

Best practices and style guide for implementing Python functions and methods.


## Architecture

Avoid side-effects. Most functions and methods should be pure or at least
provide local reasoning. Leave the most egregious side effects either to the
framework or to an outer layer of the application.

For reference, the list shows effects from best to worst. 

* no side effects, pure function (best).
* logging.
* local mutation of self.
* local mutation of input args.
* caching.
* print and input.
* file I/O, 
* database access.
* image display, sound, complex rendering of markup.
* network access.
* global mutation of application behavior (worst).

Try to keep implementations as high as possible in this list.

## Testing

Pure functions should be tested with examples in unit tests. If the function
respect some invariant, use property-based testing to generate a wide range of 
inputs. Python's `hypothesis` library is a good choice for this.

Functions up to "local mutation of input args" can be tested with no special setup.
Always use property based tests, when an invariant is known. 

Functions that use caching should usually reset the cache before each test.

Functions with simple IO should capture output using contextlib's 
`redirect_stdout` and `redirect_stderr` and mocking for `input`.

Functions that read files should use mocking and functions that write files
should do so in temporary directories.

Functions that access databases should use transactions and rollbacks to avoid 
leaving the database in a dirty state. Many frameworks provide built-in support 
for this via pytest fixtures.

Functions that produces complex multimedia usually should be tested via approval
testing. Python have the approvaltests.Python library for this.

Network access should usually be mocked in unit tests and tested in integration 
tests.

When a function produces a global mutation of application behavior, it should 
should also provide a snapshot mechanism that restore the application to its 
previous state. Ideally it should be done using context managers. Ask the user
if this mechanism should be exposed as a public API or not.


## Coding style

Follow PEP 8. Always type input and output parameters. If the function do not
change the input args, prefer abstract types over concrete ones, e.g., use 
"Iterable" instead of "list", "Mapping" instead of "dict", etc. Never use "Any",
unless stricly needed. 

## Docstrings

Use google style docstrings. Do not repeat the types in the docstring. Document
any possible exceptions raised by the function. Document the return value, 
unless it is None. 

Unless the function is a one-liner, the docstring triple quotes should be on
their own lines. One-liners documentation should use single double quotes, e.g.,
`"This is a one-liner docstring."`.

The first line of the docstring should be a short summary of the function's
purpose. If there are more details, they should be included after a blank line.

Public functions that do not produce side effects should be documented with a
doctest example. Skip the test if it is too complex or requires too much
external dependencies or preparation.


## Arguments 

Python accepts arguments by position or by name. If it has an obvious prefered 
argument, the function should require it to be passed by position. Do so
by using a leading positional-only argument, e.g., `def f(x, /, y, z)`.

Functions with more than 3 arguments should use keyword-only arguments for the
less important ones. Also, it should use keyword-only arguments for any argument
with the same types if they do not share an obvious prefered order. For instance

```python

def function(name: str, role: str): 
    ...
```

should be refactored to

```python
def function(*, name: str, role: str):
    ...
```

Boolean flags should almost always be keyword-only arguments and should have a
default value of `False`. It should always possible to rename the flag so the
default is False. For instance, add a `no_` prefix to the flag name, e.g., `def
f(x, *, no_y=False)`.


## Overloads

Do not abuse of `@overload.` It usually should be used only for type narrowing
so we can type it more precisely instead of using `Any` or too broad types.

For instance, a dict-like get() function can be typed better with overloads:

```python
@overload
def get(self, key: str) -> str | None: ...

@overload
def get(self, key: str, *, default: str) -> str: ...

def get(self, key: str, *, default: str | None = None) -> str | None:
    ...
```

If a default is provided, the overload removes `None` from the return since we
known it will always return a `str`. 
