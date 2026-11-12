import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../useFetch";
import {
  buttonClass, CategoryBadge, EmptyState, ErrorBox, ghostButtonClass, inputClass, Loading, Pagination,
} from "../components";
import { fmt } from "../utils";

const PAGE_SIZE = 25;
const EMPTY = { q: "", min_radius: "", max_radius: "", hostname: "" };

export default function Planets() {
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();

  // The URL is the source of truth, so filtered views can be bookmarked and shared.
  const filters = {
    q: params.get("q") ?? "",
    min_radius: params.get("min_radius") ?? "",
    max_radius: params.get("max_radius") ?? "",
    hostname: params.get("hostname") ?? "",
  };
  const page = Math.max(1, Number(params.get("page")) || 1);

  const [draft, setDraft] = useState(filters); // what is typed in the form, before Apply
  const [selected, setSelected] = useState([]); // names ticked for comparison

  const { data, loading, error, reload } = useFetch(
    (signal) => api.searchPlanets({ ...filters, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }, signal),
    [params.toString()]
  );

  function applyFilters(e) {
    e.preventDefault();
    const next = new URLSearchParams();
    Object.entries(draft).forEach(([key, value]) => {
      if (value.trim() !== "") next.set(key, value.trim());
    });
    setParams(next); // no page parameter, so it goes back to page 1
  }

  function resetFilters() {
    setDraft(EMPTY);
    setParams({});
  }

  function goToPage(p) {
    const next = new URLSearchParams(params);
    next.set("page", String(p));
    setParams(next);
  }

  function toggle(name) {
    setSelected((current) =>
      current.includes(name)
        ? current.filter((n) => n !== name)
        : current.length < 4
          ? [...current, name]
          : current
    );
  }

  function compare() {
    const next = new URLSearchParams();
    selected.forEach((name) => next.append("names", name));
    navigate(`/compare?${next}`);
  }

  const field = (key, props) => (
    <input
      className={`${inputClass} w-full`}
      value={draft[key]}
      onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
      {...props}
    />
  );

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white">Planets</h1>

      <form onSubmit={applyFilters} className="mt-4 grid gap-3 md:grid-cols-5">
        {field("q", { placeholder: "Planet name contains…" })}
        {field("hostname", { placeholder: "Exact host star, e.g. TRAPPIST-1" })}
        {field("min_radius", { type: "number", min: 0, step: "any", placeholder: "Min radius (R⊕)" })}
        {field("max_radius", { type: "number", min: 0, step: "any", placeholder: "Max radius (R⊕)" })}
        <div className="flex gap-2">
          <button className={buttonClass}>Apply</button>
          <button type="button" className={ghostButtonClass} onClick={resetFilters}>Reset</button>
        </div>
      </form>

      {selected.length > 0 && (
        <div className="mt-4 flex items-center gap-3 rounded-lg border border-sky-900 bg-sky-950/40 p-3 text-sm">
          <span>{selected.length} selected (max 4)</span>
          <button className={buttonClass} disabled={selected.length < 2} onClick={compare}>
            Compare
          </button>
          <button className={ghostButtonClass} onClick={() => setSelected([])}>Clear</button>
        </div>
      )}

      <div className="mt-6">
        {error && <ErrorBox error={error} onRetry={reload} />}
        {!error && !data && <Loading />}
        {!error && data && data.items.length === 0 && (
          <EmptyState>No planets match these filters. Try widening the radius range.</EmptyState>
        )}

        {!error && data && data.items.length > 0 && (
          <div className={loading ? "opacity-60 transition-opacity" : ""}>
            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-3 py-2" />
                    <th className="px-3 py-2">Name</th>
                    <th className="px-3 py-2">Type</th>
                    <th className="px-3 py-2">Radius (R⊕)</th>
                    <th className="px-3 py-2">Mass (M⊕)</th>
                    <th className="px-3 py-2">Period (days)</th>
                    <th className="px-3 py-2">Host star</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((p) => (
                    <tr key={p.planet_id} className="border-t border-slate-800 hover:bg-slate-900/60">
                      <td className="px-3 py-2">
                        <input
                          type="checkbox"
                          aria-label={`Select ${p.name} for comparison`}
                          checked={selected.includes(p.name)}
                          onChange={() => toggle(p.name)}
                        />
                      </td>
                      <td className="px-3 py-2">
                        <Link to={`/planets/${encodeURIComponent(p.name)}`} className="text-sky-400 hover:underline">
                          {p.name}
                        </Link>
                      </td>
                      <td className="px-3 py-2"><CategoryBadge category={p.category} /></td>
                      <td className="px-3 py-2">{fmt(p.radius_earth)}</td>
                      <td className="px-3 py-2">
                        {p.mass_provenance === "M-R relationship" && p.mass_earth !== null ? "~" : ""}
                        {fmt(p.mass_earth)}
                      </td>
                      <td className="px-3 py-2">{fmt(p.orbital_period_days)}</td>
                      <td className="px-3 py-2">
                        {p.star ? (
                          <Link to={`/stars/${p.star_id}`} className="text-sky-400 hover:underline">
                            {p.star.hostname}
                          </Link>
                        ) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-2 text-xs text-slate-500">~ means the mass is estimated from the radius, not measured.</p>
            <Pagination
              page={page}
              pageCount={Math.max(1, Math.ceil(data.total / PAGE_SIZE))}
              total={data.total}
              onPage={goToPage}
              loading={loading}
            />
          </div>
        )}
      </div>
    </div>
  );
}