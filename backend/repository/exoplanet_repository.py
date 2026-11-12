from backend.database.connection import get_connection
from backend.models.planet import Planet
from backend.models.star import Star


class PlanetNotFoundError(Exception):
    pass

class StarNotFoundError(Exception):
    pass

class ExoplanetRepository:
    # Protected attribute
    _base_sql= """
            SELECT p.planet_id, p.pl_name, p.discoverymethod, p.disc_year, 
		    p.pl_bmassprov, p.pl_rade, p.pl_bmasse, p.pl_orbper, 
            p.pl_orbsmax, p.pl_orbeccen, p.pl_eqt, p.pl_insol, p.star_id, s.hostname, s.st_teff, s.st_rad, 
		    s.st_mass, s.st_met, s.st_spectype, s.sy_dist
            FROM planets AS p INNER JOIN stars AS s ON p.star_id = s.star_id      
        """
    _base_star_sql = """
        SELECT s.star_id, s.hostname, s.st_teff, s.st_rad, s.st_mass,
               s.st_met, s.st_spectype, s.sy_dist
        FROM stars AS s
    """
        
    def _row_to_star(self, row:dict) -> Star:
        star = Star(
        star_id=row["star_id"],
        hostname=row["hostname"],
        temperature_k=row["st_teff"],
        radius_solar=row["st_rad"],
        mass_solar=row["st_mass"],
        metallicity=row["st_met"],
        spectral_type=row["st_spectype"], 
        distance_pc=row["sy_dist"])
        
        return star
            

    def _row_to_planet(self, row: dict) -> Planet:
        star = self._row_to_star(row)
        
        planet = Planet(
            planet_id=row["planet_id"],
            name=row["pl_name"],
            star_id=row["star_id"],
            discovery_method=row["discoverymethod"], 
            discovery_year=row["disc_year"],
            mass_provenance=row["pl_bmassprov"],
            radius_earth=row["pl_rade"], 
            mass_earth=row["pl_bmasse"], 
            orbital_period_days=row["pl_orbper"],
            semi_major_axis_au=row["pl_orbsmax"],
            eccentricity=row["pl_orbeccen"],
            equilibrium_temp_k=row["pl_eqt"],
            insolation=row["pl_insol"],
            star=star)

        return planet
    
    def _fetch_rows(self, sql: str, params: tuple = ()) -> list[dict]:
        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, params)
            return cursor.fetchall()
                         
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()


    def get_planet_by_name(self, name) -> Planet:
        sql = self._base_sql + " WHERE p.pl_name = %s"
        rows = self._fetch_rows(sql, (name,))

        if not rows:
            raise PlanetNotFoundError(f"No planet named '{name}'")

        return self._row_to_planet(rows[0])

                
    def get_all_planets(self) -> list[Planet]:
        sql = self._base_sql + " ORDER BY p.pl_name"
        rows = self._fetch_rows(sql)

        planets = []
        for row in rows:
            planet = self._row_to_planet(row)
            planets.append(planet)

        return planets


    def get_planets_by_radius_range(self, min_radius: float, max_radius: float) -> list[Planet]:
        if max_radius < min_radius:
            raise ValueError("Maximum radius cannot be smaller than minimum radius")
        
        sql = self._base_sql + " WHERE pl_rade BETWEEN %s AND %s ORDER BY p.pl_rade;"
        rows = self._fetch_rows(sql, (min_radius, max_radius))
            
        planets = []
        for row in rows:
            planet = self._row_to_planet(row)
            planets.append(planet)

        return planets
    
    
    def get_planets_by_star(self, hostname: str) -> list[Planet]:
        sql = self._base_sql + " WHERE s.hostname = %s ORDER BY p.pl_name;"
        rows = self._fetch_rows(sql, (hostname,))
            
        planets = []
        for row in rows:
            planet = self._row_to_planet(row)
            planets.append(planet)

        return planets
    
    
    def get_largest_planet(self) -> Planet:
        sql = self._base_sql + " ORDER BY p.pl_rade DESC LIMIT 1;"
        rows = self._fetch_rows(sql)
            
        return self._row_to_planet(rows[0])
    
    
    def get_smallest_planet(self) -> Planet:
        sql = self._base_sql + " WHERE p.pl_rade IS NOT NULL ORDER BY p.pl_rade ASC LIMIT 1;"
        rows = self._fetch_rows(sql)
            
        return self._row_to_planet(rows[0])
    
    
    def count_planets(self) -> int:
        sql = "SELECT COUNT(*) AS total FROM planets;"
        rows = self._fetch_rows(sql)
        
        return rows[0]["total"]
    
    
    def get_planets_page(self, limit: int, offset: int) ->list[Planet]:
        sql = self._base_sql + " ORDER BY p.pl_name LIMIT %s OFFSET %s;"
        rows = self._fetch_rows(sql, (limit, offset))
        
        planets = []
        for row in rows:
            planet = self._row_to_planet(row)
            planets.append(planet)
        
        return planets
      
                
    def _build_filters(self, q=None, min_radius=None, max_radius=None, hostname=None):
        conditions = []
        params = []

        if q is not None:
            conditions.append("p.pl_name LIKE %s")
            params.append(f"%{q}%")
        if min_radius is not None:
            conditions.append("p.pl_rade >= %s")
            params.append(min_radius)
        if max_radius is not None:
            conditions.append("p.pl_rade <= %s")
            params.append(max_radius)
        if hostname is not None:
            conditions.append("s.hostname = %s")
            params.append(hostname)

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        return where, params


    def search_planets(self, q=None, min_radius=None, max_radius=None, hostname=None, limit=50, offset=0) -> list[Planet]:
        where, params = self._build_filters(q, min_radius, max_radius, hostname)
        sql = self._base_sql + where + " ORDER BY p.pl_name LIMIT %s OFFSET %s"
        rows = self._fetch_rows(sql, tuple(params + [limit, offset]))
        return [self._row_to_planet(row) for row in rows]


    def count_search(self, q=None, min_radius=None, max_radius=None, hostname=None) -> int:
        where, params = self._build_filters(q, min_radius, max_radius, hostname)
        sql = (
            "SELECT COUNT(*) AS total "
            "FROM planets AS p INNER JOIN stars AS s ON p.star_id = s.star_id"
            + where
        )
        rows = self._fetch_rows(sql, tuple(params))
        return rows[0]["total"]
    
    
    def get_star_by_id(self, star_id: int) -> Star:
        
        if star_id <= 0:
            raise StarNotFoundError(f"No star with ID less than 1 exists.")
        
        sql = self._base_star_sql + " WHERE star_id = %s;"
        rows = self._fetch_rows(sql, (star_id,))
        
        if rows is None:
            raise StarNotFoundError(f"No star with id:{star_id} exists.")
        
        return self._row_to_star(rows[0])
    
    
    def get_planets_for_star(self, star_id: int) -> list[Planet]:
        """Return all planets orbiting the star with this id, sorted by name."""
        sql = self._base_sql + " WHERE p.star_id = %s ORDER BY p.pl_name"
        rows = self._fetch_rows(sql, (star_id,))
        return [self._row_to_planet(row) for row in rows]
    
    
    def count_stars(self, q=None) -> int:
        """Return how many stars match the optional name filter."""
        sql = "SELECT COUNT(*) AS total FROM stars AS s"
        params = []

        if q is not None:
            sql += " WHERE s.hostname LIKE %s"
            params.append(f"%{q}%")

        rows = self._fetch_rows(sql, tuple(params))
        return rows[0]["total"]


    def get_stars_page(self, limit: int, offset: int, q=None) -> list[Star]:
        """Return one page of stars, sorted by hostname, optionally filtered by name."""
        sql = self._base_star_sql
        params = []

        if q is not None:
            sql += " WHERE s.hostname LIKE %s"
            params.append(f"%{q}%")

        sql += " ORDER BY s.hostname LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = self._fetch_rows(sql, tuple(params))
        return [self._row_to_star(row) for row in rows]