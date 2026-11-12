import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../useFetch";
import { buttonClass, CategoryBadge, ErrorBox, inputClass, Loading } from "../components";
import { CountUp, Globe, OrbitSystem } from "../space";
import { CATEGORY_COLORS, CATEGORY_ORDER, fmt } from "../utils";

function StatCard({ label, children, note, delay = 0 }) {
  return (
    <div
      className="rise-in rounded-xl border border-white/10 bg-slate-900/50 p-4 backdrop-blur"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-white">{children}</div>
      {note && <div className="mt-1 text-xs text-slate-500">{note}</div>}
    </div>
  );
}

export default function Home() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");

  const { data, error, reload } = useFetch(
    (signal) =>
      Promise.all([api.statistics(signal), api.largestPlanet(signal), api.listStars({ limit: 1 }, signal)]),
    []
  );

  function onSearch(e) {
    e.preventDefault();
    const text = q.trim();
    navigate(text ? `/planets?q=${encodeURIComponent(text)}` : "/planets");
  }

  if (error) return <ErrorBox error={error} onRetry={reload} />;
  if (!data) return <Loading />;

  const [stats, largest, stars] = data;
  const largestColor = CATEGORY_COLORS[largest.category] ?? CATEGORY_COLORS.Unknown;

  return (
    <div className="space-y-12">
      <section className="grid items-center gap-10 md:grid-cols-2">
        <div className="rise-in">
          <p className="text-xs uppercase tracking-[0.3em] text-sky-300/80">NASA Exoplanet Archive</p>
          <h1 className="mt-3 text-4xl font-semibold leading-tight text-white md:text-5xl">
            Explore{" "}
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: "linear-gradient(90deg, #7dd3fc, #a5b4fc, #f0abfc)" }}
            >
              <CountUp value={stats.total_planets} /> worlds
            </span>{" "}
            beyond our Sun
          </h1>
          <p className="mt-4 max-w-md text-slate-400">
            Search confirmed exoplanets, meet their host stars, and compare them side by side.
          </p>
          <form onSubmit={onSearch} className="mt-6 flex max-w-md gap-2">
            <input
              className={`${inputClass} w-full`}
              placeholder="Search planets, e.g. TRAPPIST"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <button className={buttonClass}>Search</button>
          </form>
        </div>

        <div className="rise-in" style={{ animationDelay: "200ms" }}>
          <OrbitSystem hostname="TRAPPIST-1" />
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Planets" delay={100}><CountUp value={stats.total_planets} /></StatCard>
        <StatCard label="Host stars" delay={200}><CountUp value={stars.total} /></StatCard>
        <StatCard label="Median radius" note={`mean ${fmt(stats.radius?.mean)} R⊕`} delay={300}>
          {fmt(stats.radius?.median)} R⊕
        </StatCard>
        <StatCard label="Known radius" note="planets with a measured size" delay={400}>
          <CountUp value={stats.radius?.count ?? 0} />
        </StatCard>
      </section>

      <section className="rise-in rounded-xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur" style={{ animationDelay: "300ms" }}>
        <h2 className="text-lg font-medium text-white">Planet types</h2>
        <div className="mt-3 flex h-4 overflow-hidden rounded-full bg-slate-800">
          {CATEGORY_ORDER.map((c) => (
            <div
              key={c}
              title={`${c}: ${stats.category_counts[c]}`}
              style={{
                width: `${(stats.category_counts[c] / stats.total_planets) * 100}%`,
                backgroundColor: CATEGORY_COLORS[c],
              }}
            />
          ))}
        </div>
        <ul className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm text-slate-400">
          {CATEGORY_ORDER.map((c) => (
            <li key={c} className="flex items-center gap-2">
              <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[c] }} />
              {c}: {stats.category_counts[c].toLocaleString()}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-slate-500">
          A few very large planets pull the mean radius up, so the median is the better "typical" value.
        </p>
      </section>

      <section className="rise-in flex items-center gap-6 rounded-xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur" style={{ animationDelay: "400ms" }}>
        <Globe color={largestColor} size={110} />
        <div>
          <div className="text-xs uppercase tracking-wide text-slate-400">Largest planet in the archive</div>
          <Link to={`/planets/${encodeURIComponent(largest.name)}`} className="text-2xl text-sky-300 hover:underline">
            {largest.name}
          </Link>
          <div className="mt-1 flex items-center gap-2 text-sm text-slate-400">
            {fmt(largest.radius_earth)} Earth radii <CategoryBadge category={largest.category} />
          </div>
        </div>
      </section>
    </div>
  );
}