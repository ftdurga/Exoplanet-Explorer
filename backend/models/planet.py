from enum import Enum
from typing import Optional
from dataclasses import dataclass
from backend.models.star import Star

# Enum class for planet category based on radius
class PlanetCategory(Enum):
    EARTH_LIKE = "Earth-like"
    SUPER_EARTH = "Super-Earth"
    NEPTUNE_LIKE = "Neptune-like"
    GIANT = "Giant"
    UNKNOWN = "Unknown"


@dataclass   
class Planet:
    
    planet_id: int
    name: str
    star_id: int
    discovery_method: str
    discovery_year: int
    mass_provenance: str 
    radius_earth: Optional[float] = None
    mass_earth: Optional[float] = None 
    orbital_period_days: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    eccentricity: Optional[float] = None
    equilibrium_temp_k: Optional[float] = None
    insolation: Optional[float] = None
    star: Optional[Star] = None


    @property
    def category(self) -> PlanetCategory:
        if self.radius_earth is None:
            return PlanetCategory.UNKNOWN
        elif self.radius_earth < 1.25:
            return PlanetCategory.EARTH_LIKE
        elif self.radius_earth < 2.0:
            return PlanetCategory.SUPER_EARTH
        elif self.radius_earth < 6.0:
            return PlanetCategory.NEPTUNE_LIKE
        else:
            return PlanetCategory.GIANT
     
    def __str__(self) -> str:
        if self.radius_earth is None:
            return f"Name: {self.name}"
        
        return f"Name: {self.name} | Radius: {self.radius_earth}| Catgory: {self.category.value}"
    
    
    