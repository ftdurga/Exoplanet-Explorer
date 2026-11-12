import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../useFetch";
import { CategoryBadge, ErrorBox, Fact, Loading, Orb } from "../components";
import { fmt } from "../utils";

export default function StarDetail() {
  const { id } = useParams();
  const { data: star, error, reload } = useFetch((signal) => api.star(id, signal), [id]);

  if (error) {
    return (
      <div className="space-y-4">
        <ErrorBox error={error} onRetry={error.status === 404 ? undefined : reload} />
        <Link to="/planets" className="text-sky-400 hover:underline">← Back to planets</Link>
      </div>
    );
  }
  if (!star) return <Loading />;

  return (
    <div className="space-y-6">
      <Link to="/planets" className="text-sm text-sky-400 hover:underline">← All planets</Link>
      <h1 className="text-3xl font-semibold text-white">{star.hostname}</h1>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <Fact label="Temperature">{fmt(star.temperature_k, 0)} K</Fact>
        <Fact label="Radius">{fmt(star.radius_solar)} R☉</Fact>
        <Fact label="Mass">{fmt(star.mass_solar)} M☉</Fact>
        <Fact label="Metallicity">{fmt(star.metallicity)}</Fact>
        <Fact label="Spectral type">{star.spectral_type ?? "—"}</Fact>
        <Fact label="Distance">{fmt(star.distance_pc)} parsecs</Fact>
      </section>

      <section>
        <h2 className="text-lg font-medium text-white">
          {star.planet_count} {star.planet_count === 1 ? "planet" : "planets"}
        </h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {star.planets.map((p) => (
            <Link
              key={p.planet_id}
              to={`/planets/${encodeURIComponent(p.name)}`}
              className="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-900/60 p-4 hover:border-slate-600"
            >
              <Orb radius={p.radius_earth} category={p.category} />
              <div>
                <div className="text-sky-400">{p.name}</div>
                <div className="text-sm text-slate-400">{fmt(p.radius_earth)} R⊕</div>
                <CategoryBadge category={p.category} />
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}