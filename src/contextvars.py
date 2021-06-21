# Copyright (c) 2015-present MagicStack Inc.  http://magic.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections.abc
import threading


__all__ = ('ContextVar', 'Context', 'Token', 'copy_context')


_NO_DEFAULT = object()


class ContextMeta(type(collections.abc.Mapping)):

    # contextvars.Context is not subclassable.

    def __new__(mcls, names, bases, dct):
        cls = super().__new__(mcls, names, bases, dct)
        if cls.__module__ != 'contextvars' or cls.__name__ != 'Context':
            raise TypeError("type 'Context' is not an acceptable base type")
        return cls


class Context(collections.abc.Mapping, metaclass=ContextMeta):

    def __init__(self):
        self._data = dict()
        self._prev_context = None

    def run(self, callable, *args, **kwargs):
        if self._prev_context is not None:
            raise RuntimeError(
                'cannot enter context: {} is already entered'.format(self))

        self._prev_context = _get_context()
        try:
            _set_context(self)
            return callable(*args, **kwargs)
        finally:
            _set_context(self._prev_context)
            self._prev_context = None

    def copy(self):
        new = Context()
        new._data = self._data
        return new

    def __getitem__(self, var):
        if not isinstance(var, ContextVar):
            raise TypeError(
                "a ContextVar key was expected, got {!r}".format(var))
        return self._data[var]

    def __contains__(self, var):
        if not isinstance(var, ContextVar):
            raise TypeError(
                "a ContextVar key was expected, got {!r}".format(var))
        return var in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


class ContextVarMeta(type):

    # contextvars.ContextVar is not subclassable.

    def __new__(mcls, names, bases, dct):
        cls = super().__new__(mcls, names, bases, dct)
        if cls.__module__ != 'contextvars' or cls.__name__ != 'ContextVar':
            raise TypeError("type 'ContextVar' is not an acceptable base type")
        return cls

    def __getitem__(cls, name):
        return


class ContextVar(metaclass=ContextVarMeta):

    def __init__(self, name, *, default=_NO_DEFAULT):
        if not isinstance(name, str):
            raise TypeError("context variable name must be a str")
        self._name = name
        self._default = default

    @property
    def name(self):
        return self._name

    def get(self, default=_NO_DEFAULT):
        ctx = _get_context()
        try:
            return ctx[self]
        except KeyError:
            pass

        if default is not _NO_DEFAULT:
            return default

        if self._default is not _NO_DEFAULT:
            return self._default

        raise LookupError

    def set(self, value):
        ctx = _get_context()
        data = ctx._data
        try:
            old_value = data[self]
        except KeyError:
            old_value = Token.MISSING

        updated_data = data.copy()
        updated_data[self] = value
        ctx._data = updated_data
        return Token(ctx, self, old_value)

    def reset(self, token):
        if token._used:
            raise RuntimeError("Token has already been used once")

        if token._var is not self:
            raise ValueError(
                "Token was created by a different ContextVar")

        if token._context is not _get_context():
            raise ValueError(
                "Token was created in a different Context")

        ctx = token._context
        if token._old_value is Token.MISSING:
            ctx._data = ctx._data.delete(token._var)
        else:
            ctx._data = ctx._data.copy()
            ctx._data[token._var] = token._old_value

        token._used = True

    def __repr__(self):
        r = '<ContextVar name={!r}'.format(self.name)
        if self._default is not _NO_DEFAULT:
            r += ' default={!r}'.format(self._default)
        return r + ' at {:0x}>'.format(id(self))


class TokenMeta(type):

    # contextvars.Token is not subclassable.

    def __new__(mcls, names, bases, dct):
        cls = super().__new__(mcls, names, bases, dct)
        if cls.__module__ != 'contextvars' or cls.__name__ != 'Token':
            raise TypeError("type 'Token' is not an acceptable base type")
        return cls


class Token(metaclass=TokenMeta):

    MISSING = object()

    def __init__(self, context, var, old_value):
        self._context = context
        self._var = var
        self._old_value = old_value
        self._used = False

    @property
    def var(self):
        return self._var

    @property
    def old_value(self):
        return self._old_value

    def __repr__(self):
        r = '<Token '
        if self._used:
            r += ' used'
        r += ' var={!r} at {:0x}>'.format(self._var, id(self))
        return r


def copy_context():
    return _get_context().copy()


def _get_context():
    import asyncio.tasks
    try:
        task = asyncio.tasks.current_task()
        ctx = getattr(task, '_task_context', None)
    except RuntimeError:
        ctx = None

    if ctx is None:
        ctx = getattr(_state, 'context', None)
    if ctx is None:
        ctx = Context()
        _state.context = ctx
    return ctx


def _set_context(ctx):
    _state.context = ctx


_state = threading.local()
