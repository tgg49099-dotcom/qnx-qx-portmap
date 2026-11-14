"""Point d'entree : ``python3 -m qnx_portmap``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
