"""
Jev Gem Scan — a DEMO / EDUCATIONAL router that scores simulated token
launches GEM or RUG using a mocked "TypeSafe Jev" decision model.

This package places NO real trades, holds NO wallet or keys, and makes NO
network calls. See README.md for the full disclaimer.
"""

__version__ = "1.0.0"

from .generator import generate_launch          # noqa: F401
from .jev_stub import call_jev_api, GEM_CONFIDENCE_THRESHOLD  # noqa: F401
from .router import route_launch, load_config    # noqa: F401
from .logbook import log_scan                     # noqa: F401
