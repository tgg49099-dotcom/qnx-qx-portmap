"""QX PORTMAP - state of the QNX symbols in the official 8.0 documentation.

The package reads a QNX documentation corpus frozen in the repository and
answers, for every symbol given, one single question: is the symbol
documented in 8.0, described elsewhere, absent, or unknown to the corpus?

No network access is made at runtime.
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
