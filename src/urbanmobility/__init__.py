"""UrbanMobility: A Python package for processing, analyzing, and visualizing urban mobility data"""

from . import buildings
from . import io
from . import maps
from . import mobility
from . import spatial
from .config import DEFAULT_CRS, CRS_WGS84

__version__ = "0.1.0"

__all__ =[
    "__version__",
    "buildings",
    "io",
    "maps",
    "mobility",
    "spatial",
    "DEFAULT_CRS",
    "CRS_WGS84",
]