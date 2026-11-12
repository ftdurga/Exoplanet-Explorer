import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../useFetch";
import { buttonClass, CategoryBadge, EmptyState, ErrorBox, inputClass, Loading, Orb } from "../components";
import { fmt } from "../utils";

// Each row of the comparison table. `get` reads the value from a planet.
const METRICS = [
  { label: "Radius (R⊕)", get: (p) => p.radius_earth, bar: true },
  { label: "Mass (M⊕)", get: (p) => p.mass_earth, bar: true },
  { label: "Orbital period (days)", get: (p) => p.orbital_period_days, bar: true },
  { label: "Distance from star (AU)", get: (p) => p.semi_major_axis_au, bar: true },
  { label: "Equilibrium temp (K)", get: (p) => p.equilibrium_temp_k, bar: true },
  { label: "Starlight (Earth = 1)", get: (p) => p.insolation, bar: true },
  { label: "Host star temp (K)", get: (p) => p.star?.temperature_k ?? null, bar: true },
  { label: "Discovered", get: (p) => p.discovery_year, bar: false, raw: true },
];

export default function Compare() {
  const [params, setParams] = useSearchParams();
  const names = params.getAll("names"); // the URL holds the list, so a comparison can be shared
  const [draft, setDraft] = useState("");
  const [inputError, setInputError] = useState("");

  const { data, loading, error, reload } = useFetch(
    (signal) => (names.length >= 2 ? api.comparePlanets(names, signal) : Promise.resolve(null)),
    [names.join("\n")]
  );

  function setNames(next) {
    const sp = new URLSearchParams();
    next.forEach((n) => sp.append("names", n));
    setParams(sp);
  }

  function add(e) {
    e.preventDefault();
    const name = draft.trim();
    if (!name) return;
    if (names.includes(name)) return setInputError("That planet is already in the list.");
    if (names.length >= 4) return setInputError("You can compare at most 4 planets.");
    setInputError("");
    setDraft("");
    setNames([...names, name]);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-white">Compare planets</h1>

      <form onSubmit={add} className="flex flex-wrap gap-2">
        <input
          className={`${inputClass} w-full max-w-sm`}
          placeholder="Exact planet name, e.g. TRAPPIST-1 e"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button className={buttonClass}>Add</button>
      </form>
      {inputError && <p className="text-sm text-red-300">{inputError}</p>}

      <div className="flex flex-wrap gap-2">
        {names.map((n) => (
          <span key={n} className="flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1 text-sm">
            {n}
            <button
              aria-label={`Remove ${n}`}
              className="text-slate-500 hover:text-white"
              onClick={() => setNames(names.filter((x) => x !== n))}
            >
              ×
            </button>
          </span>
        ))}
      </div>

      {names.length < 2 && (
        <EmptyState>
          Add at least two planets to compare them. You can also tick planets in the{" "}
          <Link to="/planets" className="text-sky-400 hover:underline">planet browser</Link>.
        </EmptyState>
      )}

      {names.length >= 2 && error && <ErrorBox error={error} onRetry={reload} />}
      {names.length >= 2 && !error && !data && <Loading />}

      {names.length >= 2 && !error && data && (
        <div className={loading ? "opacity-60" : ""}>
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-slate-900">
                  <th className="px-4 py-3" />
                  {data.planets.map((p) => (
                    <th key={p.planet_id} className="px-4 py-3 align-bottom">
                      <Orb radius={p.radius_earth} category={p.category} />
                      <Link to={`/planets/${encodeURIComponent(p.name)}`} className="mt-2 block text-sky-400 hover:underline">
                        {p.name}
                      </Link>
                      <CategoryBadge category={p.category} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-slate-800">
                  <th className="px-4 py-3 text-xs font-normal uppercase tracking-wide text-slate-500">Host star</th>
                  {data.planets.map((p) => (
                    <td key={p.planet_id} className="px-4 py-3">
                      {p.star ? (
                        <Link to={`/stars/${p.star_id}`} className="text-sky-400 hover:underline">{p.star.hostname}</Link>
                      ) : "—"}
                    </td>
                  ))}
                </tr>
                {METRICS.map((m) => {
                  const values = data.planets.map(m.get);
                  const max = Math.max(...values.filter((v) => v !== null && v !== undefined), 0);
                  return (
                    <tr key={m.label} className="border-t border-slate-800">
                      <th className="px-4 py-3 text-xs font-normal uppercase tracking-wide text-slate-500">{m.label}</th>
                      {values.map((v, i) => (
                        <td key={i} className="px-4 py-3 align-top">
                          <div>{v === null || v === undefined ? "—" : m.raw ? v : fmt(v, 3)}</div>
                          {m.bar && v !== null && v !== undefined && max > 0 && (
                            <div className="mt-1 h-1.5 rounded bg-slate-800">
                              <div className="h-1.5 rounded bg-sky-500" style={{ width: `${(v / max) * 100}%` }} />
                            </div>
                          )}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Bars are linear within each row, so one extreme value can make the others look small.
          </p>
        </div>
      )}
    </div>
  );
}