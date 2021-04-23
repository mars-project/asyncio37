asyncio37
---------

This package replaces default implementation of ``asyncio`` in Python 3.6 with
implementation in Python 3.7. A ``contextvars`` library 
`from MagicStack <https://github.com/MagicStack/contextvars>`_ is also
included to make sure the package functions well.

Notes
=====
After installation, this package will replace the builtin implementation of
``asyncio`` in Python 3.6. To use the builtin implementation, you have to
uninstall this package or add an environment variable ``USE_BUILTIN_ASYNCIO=1``
to avoid loading the replacements.

As ``PyThreadState`` in Python 3.6 does not include an unique identifier,
we cannot cache it when calling ``get_running_loop``. Hence the performance
of the library may be degraded comparing to the original module in Python 3.7.

License
=======
The whole package is released under Apache License 2.0. Codes under ``asyncio``
module is copied from Python 3.7 source which is released under PSF License
Agreement with minimal modifications. Codes in ``contextvars.py`` is copied from
MagicStack codes released under Apache License 2.0.
