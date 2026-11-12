from dataclasses import dataclass
from typing import Optional

@dataclass
class Star:

    star_id: int 
    hostname: str
    temperature_k: Optional[float] = None
    radius_solar: Optional[float] = None
    mass_solar: Optional[float] = None
    metallicity: Optional[float] = None
    spectral_type: Optional[str] = None
    distance_pc: Optional[float] = None

    
    