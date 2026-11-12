# Exoplanet Explorer

A full-stack data application for exploring confirmed exoplanets and their
host stars. It is built on the NASA Exoplanet Archive and covers 6,451
planets orbiting 4,847 stars (Planetary Systems Composite Parameters,
downloaded 2026-10-31).

<img width="632" height="308" alt="image" src="https://github.com/user-attachments/assets/24526f83-9557-4ee4-a28f-a6120d64523c" />

## Features

- Search and filter planets by name, radius range and host star, with pagination
- Planet profiles with physical data, plus host star pages listing all of a star's planets
- Side-by-side comparison of 2 to 4 planets
- Statistics and charts: radius, mass and orbital period distributions,
  radius against orbit length, and discoveries per year
- Filters and comparisons live in the URL, so any view can be shared


## Tech stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| Database | MySQL 8, `mysql-connector-python` (hand-written SQL, no ORM) |
| Data loading | pandas |
| Frontend | React (Vite), Tailwind CSS, React Router, Recharts |
| Testing | pytest |

## Architecture

```text
MySQL -> Repository -> Service -> API routes -> React frontend
```

| Layer | Responsibility | Does not |
| --- | --- | --- |
| Models | `Planet`, `Star`, `PlanetCategory` (dataclasses and an Enum) | Know a database exists |
| Repository | All SQL; turns rows into model objects | Contain business rules |
| Service | Rules, statistics, histograms | Know SQL or HTTP |
| API | Validation, status codes, JSON schemas | Contain SQL or calculations |

Each layer talks only to the one below it. Errors travel up as domain
exceptions (`PlanetNotFoundError`, `InvalidQueryError`,
`DatabaseConnectionError`) and are translated to HTTP responses (404, 422,
503) in one place, `api/errors.py`.

```text
backend/
├── models/        # dataclasses and enums
├── database/      # connection handling
├── repository/    # SQL and row-to-object mapping
├── services/      # calculations and rules
├── api/           # routes, schemas, error handlers
├── scripts/       # CSV loader
├── sql/           # table creation and transformation scripts
├── data/          # NASA source CSV
└── tests/         # pytest suite
frontend/          # React app
```

## Getting started

Requirements: Python 3.11 or newer, Node 20 or newer, MySQL 8.

### 1. Backend

Run these commands from the project root:

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
```

Create an empty MySQL database, then copy `.env.example` to `.env` and fill
in your connection details.

**2. Build the database** (from `backend/`)

```bash
python -m scripts.build_database
```

This creates the tables, loads the CSV into a staging table and builds the
`stars` and `planets` tables. It is safe to re-run.

### 3. Run the API

```bash
python -m uvicorn backend.main:app --reload
```

Interactive docs: <http://localhost:8000/docs>

### 4. Run the frontend

(second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The port matters: the API only allows that
origin through CORS.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/planets` | Paginated planet list |
| GET | `/planets/search` | Filter by `q`, `min_radius`, `max_radius`, `hostname` |
| GET | `/planets/largest` | Largest planet by radius |
| GET | `/planets/{name}` | One planet, with its star |
| POST | `/planets/compare` | Compare 2 to 4 planets by name |
| GET | `/stars` | Paginated star list, optional name filter |
| GET | `/stars/{star_id}` | A star and its planets |
| GET | `/statistics` | Radius summary and category counts |
| GET | `/insights/histogram` | Log-binned counts (`metric`: radius, mass, period) |
| GET | `/insights/radius-period` | Points for the radius vs period chart |
| GET | `/insights/discoveries` | Discoveries per year |

## Testing

```bash
python -m pytest -v
```

Service and API tests run against fake repositories, so they need no
database. Tests in `test_repository.py`, `test_connection.py`, `test_api.py`
and `test_insights.py` use the real database and need MySQL running with the
tables loaded. Counts in those tests are snapshots of the 2026-10-31 data.

## Data pipeline and decisions

**Staging, then clean tables.** The source CSV has one row per planet. It is
loaded into `staging_exoplanets`, then split into `stars` and `planets`
tables linked by a foreign key. The pipeline is repeatable, so a newer
download can be loaded by rerunning the steps above.

**Conflicting star values.** Star properties repeat on every planet row and
do not always agree, because each planet can cite a different publication.
[N] stars had conflicting values (**verify**). For each star I keep the row
with the most non-null star values, breaking ties alphabetically by planet
name (`ROW_NUMBER()` in `sql/03_transform.sql`).

**Missing data.** Many measurements are `NULL` in the source (50 planets
have no radius). They stay `NULL`, are `Optional` in the models, and appear
as `null` in the API. They are never replaced with zeros, and statistics
ignore them.

**Estimated masses.** [N] planets have a mass estimated from their radius
rather than measured (`mass_provenance`) (**verify**). The frontend marks
these with `~`.

**Planet categories**, by radius in Earth radii:

| Radius | Category | Planets |
| --- | --- | --- |
| < 1.25 | Earth-like | 583 |
| 1.25 to < 2.0 | Super-Earth | 1,212 |
| 2.0 to < 6.0 | Neptune-like | 2,442 |
| >= 6.0 | Giant | 2,164 |
| unknown | Unknown | 50 |

## Findings

- **Mean versus median.** Radii run from 0.31 to 87 Earth radii. The mean
  (5.84) is more than double the median (2.86), so summaries report both.
- **Two populations.** The radius histogram has two peaks: planets around
  1.8 to 3.2 Earth radii, and Jupiter-sized planets around 10 to 18.
- **Discovery spikes.** Discoveries jump in 2014 and 2016, most likely
  because large batches of Kepler candidates were confirmed in those years.
- **Detection bias.** Short orbits and large planets dominate the sample,
  partly because the main detection methods find them most easily, so the
  catalogue is not a fair picture of all planets.

## Design choices

- Hand-written SQL with parameterised queries (`%s`) to keep the
  Python-SQL link explicit and prevent SQL injection
- The service receives its repository through its constructor, so tests can
  pass in a fake (duck typing)
- Separate Pydantic response schemas, so the JSON can change independently
  of the Python models
- Pagination on every list endpoint, with a maximum page size
- Log-spaced histogram bins, because the data spans several orders of magnitude

## Limitations and next steps

- Statistics and insight endpoints load all planets on each request. That is
  fine at 6,451 rows. Caching or SQL aggregation would be the next step.
- Planet visuals are drawings scaled from the data, not photographs.
- Not deployed yet. Planned: containerised backend and a hosted frontend.
- A host-star temperature chart and a planet-type filter on the search endpoint.

## Data source

Data from the NASA Exoplanet Archive: <https://exoplanetarchive.ipac.caltech.edu>

This research has made use of the NASA Exoplanet Archive, which is operated
by the California Institute of Technology, under contract with the National
Aeronautics and Space Administration under the Exoplanet Exploration
Program.
