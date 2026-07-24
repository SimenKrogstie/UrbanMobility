"""UrbanMobility: A Python package for processing, analyzing, and visualizing urban mobility data"""

from . import buildings
from . import mobility
from . import spatial
from . import io
from . import maps
from .config import DEFAULT_CRS, CRS_WGS84

__version__ = "0.1.0"

__all__ =[
    "__version__",
    "buildings",
    "mobility",
    "spatial",
    "io",
    "maps",
    "DEFAULT_CRS",
    "CRS_WGS84",
]