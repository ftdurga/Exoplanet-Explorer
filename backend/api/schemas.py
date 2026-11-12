from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.models.planet import PlanetCategory


class StarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    star_id: int
    hostname: str
    temperature_k: Optional[float] = None
    radius_solar: Optional[float] = None
    mass_solar: Optional[float] = None
    metallicity: Optional[float] = None
    spectral_type: Optional[str] = None
    distance_pc: Optional[float] = None


class PlanetSummaryOut(BaseModel):
    """A planet without its star, used inside a star's response."""
    model_config = ConfigDict(from_attributes=True)

    planet_id: int
    name: str
    star_id: int
    discovery_method: str
    discovery_year: int
    mass_provenance: str
    category: PlanetCategory
    radius_earth: Optional[float] = None
    mass_earth: Optional[float] = None
    orbital_period_days: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    eccentricity: Optional[float] = None
    equilibrium_temp_k: Optional[float] = None
    insolation: Optional[float] = None


class PlanetOut(PlanetSummaryOut):
    """A planet with its host star attached."""
    star: Optional[StarOut] = None


class StarDetailOut(StarOut):
    planet_count: int
    planets: list[PlanetSummaryOut]


class PlanetPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PlanetOut]


class StarPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[StarOut]
    
class RadiusSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    
class StatisticsOut(BaseModel):
    total_planets: int
    radius: Optional[RadiusSummaryOut] = None
    category_counts: dict[str, int]
    

class CompareRequest(BaseModel):
    names: list[str] = Field(min_length=2, max_length=4)

class CompareOut(BaseModel):
    planets: list[PlanetOut]
    
class HistogramBinOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    low: float
    high: float
    count: int


class ScatterPointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    radius_earth: float
    orbital_period_days: float
    category: PlanetCategory


class YearCountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    year: int
    count: int