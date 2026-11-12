import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../useFetch";
import { CategoryBadge, ErrorBox, Fact, Loading, Orb } from "../components";
import { fmt, MASS_NOTES } from "../utils";

export default function PlanetDetail() {
  const { name } = useParams(); // React Router already decodes %20 and %2B
  const { data: planet, error, reload } = useFetch((signal) => api.planet(name, signal), [name]);

  if (error) {
    return (
      <div className="space-y-4">
        <ErrorBox error={error} onRetry={error.status === 404 ? undefined : reload} />
        <Link to="/planets" className="text-sky-400 hover:underline">← Back to planets</Link>
      </div>
    );
  }
  if (!planet) return <Loading />;

  return (
    <div className="space-y-6">
      <Link to="/planets" className="text-sm text-sky-400 hover:underline">← All planets</Link>

      <header className="flex flex-wrap items-end gap-8">
        <div className="flex items-end gap-6">
          <div className="text-center">
            <Orb radius={planet.radius_earth} category={planet.category} />
            <div className="mt-1 text-xs text-slate-500">{planet.name}</div>
          </div>
          <div className="text-center">
            <Orb radius={1} category="Earth-like" />
            <div className="mt-1 text-xs text-slate-500">Earth</div>
          </div>
        </div>
        <div>
          <h1 className="text-3xl font-semibold text-white">{planet.name}</h1>
          <div className="mt-2"><CategoryBadge category={planet.category} /></div>
        </div>
      </header>
      <p className="text-xs text-slate-500">Sizes are drawn on a log scale and are not photographs.</p>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <Fact label="Radius">{fmt(planet.radius_earth, 3)} R⊕</Fact>
        <Fact label="Mass" note={MASS_NOTES[planet.mass_provenance] ?? planet.mass_provenance}>
          {fmt(planet.mass_earth)} M⊕
        </Fact>
        <Fact label="Orbital period">{fmt(planet.orbital_period_days, 3)} days</Fact>
        <Fact label="Distance from star">{fmt(planet.semi_major_axis_au, 4)} AU</Fact>
        <Fact label="Eccentricity">{fmt(planet.eccentricity, 3)}</Fact>
        <Fact label="Equilibrium temperature">{fmt(planet.equilibrium_temp_k, 0)} K</Fact>
        <Fact label="Starlight received" note="Earth = 1">{fmt(planet.insolation)}</Fact>
        <Fact label="Discovered">{planet.discovery_year} ({planet.discovery_method})</Fact>
      </section>

      {planet.star && (
        <section className="rounded-lg border border-slate-800 bg-slate-900/60 p-5">
          <div className="text-xs uppercase tracking-wide text-slate-500">Host star</div>
          <Link to={`/stars/${planet.star_id}`} className="text-xl text-sky-400 hover:underline">
            {planet.star.hostname}
          </Link>
          <div className="mt-1 text-sm text-slate-400">
            {fmt(planet.star.temperature_k, 0)} K · {fmt(planet.star.radius_solar)} R☉ · {fmt(planet.star.mass_solar)} M☉
          </div>
        </section>
      )}

      <Link to={`/compare?names=${encodeURIComponent(planet.name)}`} className="inline-block text-sky-400 hover:underline">
        Compare this planet with others →
      </Link>
    </div>
  );
}