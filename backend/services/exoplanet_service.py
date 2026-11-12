from typing import Optional
from dataclasses import dataclass
from statistics import mean, median
from backend.models.planet import Planet, PlanetCategory
from backend.models.star import Star
from backend.repository.exoplanet_repository import ExoplanetRepository
from bisect import bisect_right  
from collections import Counter

@dataclass
class RadiusSummary:
    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    
@dataclass
class Statistics:
    total_planets: int
    radius: Optional[RadiusSummary]
    category_counts: dict[PlanetCategory, int]

class InvalidQueryError(ValueError):
    """The caller asked for something the rules do not allow."""

# metric -> (planet attribute, first power of ten, last power of ten, bins per power of ten)
HISTOGRAMS = {
    "radius": ("radius_earth", -1, 2, 4),         # 0.1 to 100 Earth radii
    "mass": ("mass_earth", -2, 5, 2),             # 0.01 to 100,000 Earth masses
    "period": ("orbital_period_days", -2, 9, 1),  # 0.01 days to 1 billion days
}


@dataclass
class HistogramBin:
    low: float
    high: float
    count: int


@dataclass
class ScatterPoint:
    name: str
    radius_earth: float
    orbital_period_days: float
    category: PlanetCategory


@dataclass
class YearCount:
    year: int
    count: int
 
# service -> repository
class ExoplanetService:

    def __init__(self, repository: ExoplanetRepository):
        self._repository = repository
    
    # Average radius = Sum of available radii / Count of available radii
    def average_radius(self) -> Optional[float]:
        planets = self._repository.get_all_planets()
        sum_radius = 0
        count_planet = 0
        for p in planets:
            if p.radius_earth is not None:
                sum_radius += p.radius_earth
                count_planet += 1
        
        # Validation check
        if count_planet == 0:
            return None
        
        return sum_radius / count_planet
    
    # Count number of planets in each category
    def category_counts(self) -> dict[PlanetCategory, int]:
        category_dict = {}

        for category in PlanetCategory:
            category_dict[category] = 0
        
        planets = self._repository.get_all_planets()
        for p in planets:
            category_dict[p.category] += 1

        return category_dict
    
    # Statistical summary of all radii
    def radius_summary(self) -> Optional[RadiusSummary]:
        planets = self._repository.get_all_planets()
        all_radii = []
        for p in planets:
            if p.radius_earth is not None:
                all_radii.append(p.radius_earth)
        
        # Validation check
        if len(all_radii) == 0:
            return None
        
        return RadiusSummary(len(all_radii), min(all_radii), max(all_radii), mean(all_radii), median(all_radii))
    
    # Get planet by name -> call on repository method
    def get_planet(self, name) -> Planet:
        
        # Let PlanetNotFoundError pass through
        planet = self._repository.get_planet_by_name(name)
        return planet
    
    # List planets by pages -> call on repository method
    def list_planets(self, limit, offset) -> tuple[list[Planet], int]:
        page = self._repository.get_planets_page(limit, offset)
        total = self._repository.count_planets()
        
        return (page, total)
    
    # Search for planets using conditions -> call on repository method
    def search_planets(self, q=None, min_radius=None, max_radius=None, hostname=None, limit=50, offset=0) -> tuple[list[Planet], int]:
        
        # Input Validation check
        if min_radius is not None and max_radius is not None and min_radius > max_radius:
            raise InvalidQueryError("min_radius must not be greater than max_radius")

        planets = self._repository.search_planets(q, min_radius, max_radius, hostname, limit, offset)
        total = self._repository.count_search(q, min_radius, max_radius, hostname)
        return (planets, total)
    
    # Get the largest planet -> calls the repository method
    def get_largest_planet(self) -> Planet:
        return self._repository.get_largest_planet()
    
    # Get the star based on star_id, and planets associated to star -> calls 2 methods
    def get_star(self, star_id) -> tuple[Star, list[Planet]]:
        
        # Let StarNotFoundError pass through
        star = self._repository.get_star_by_id(star_id)
        planets = self._repository.get_planets_for_star(star_id)
        
        return (star, planets)
    
    # List all the stars - calls two methods
    def list_stars(self, q, limit, offset) -> tuple[list[Star], int]:
        stars = self._repository.get_stars_page(limit, offset, q)
        count = self._repository.count_stars(q)
        
        return (stars, count)
    
    def get_statistics(self) -> Statistics:
        return Statistics(
            total_planets=self._repository.count_planets(),
            radius=self.radius_summary(),
            category_counts=self.category_counts(),
        )        
        
    def compare_planets(self, names: list[str]) -> list[Planet]:
        if len(names) != len(set(names)):
            raise InvalidQueryError("Duplicate planet names are not allowed")
        
        planets = []
        for name in names:
            planet = self.get_planet(name)
            
            if planet is not None:
                planets.append(planet)
        
        return planets
    
    def histogram(self, metric: str) -> list[HistogramBin]:
        """Count planets in log-spaced bins. Planets with no value are skipped."""
        if metric not in HISTOGRAMS:
            raise InvalidQueryError(f"Unknown metric '{metric}'. Choose from: {', '.join(HISTOGRAMS)}")

        attribute, first, last, per_decade = HISTOGRAMS[metric]
        edges = [10 ** (first + i / per_decade) for i in range((last - first) * per_decade + 1)]
        counts = [0] * (len(edges) - 1)

        for planet in self._repository.get_all_planets():
            value = getattr(planet, attribute)
            if value is None:
                continue
            index = bisect_right(edges, value) - 1      # a value on an edge goes in the upper bin
            if 0 <= index < len(counts):
                counts[index] += 1

        return [
            HistogramBin(low=float(f"{edges[i]:.4g}"), high=float(f"{edges[i + 1]:.4g}"), count=counts[i])
            for i in range(len(counts))
        ]

    def radius_period_points(self) -> list[ScatterPoint]:
        """One point per planet that has both a radius and an orbital period."""
        return [
            ScatterPoint(p.name, p.radius_earth, p.orbital_period_days, p.category)
            for p in self._repository.get_all_planets()
            if p.radius_earth is not None and p.orbital_period_days is not None
        ]

    def discoveries_per_year(self) -> list[YearCount]:
        """Planets discovered per year, with 0 for years that had none."""
        counts = Counter(p.discovery_year for p in self._repository.get_all_planets())
        if not counts:
            return []
        return [YearCount(year, counts[year]) for year in range(min(counts), max(counts) + 1)]