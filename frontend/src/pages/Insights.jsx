import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { api } from "../api";
import { useFetch } from "../useFetch";
import { ErrorBox, Loading } from "../components";
import { CATEGORY_COLORS, CATEGORY_ORDER } from "../utils";

const AXIS = "#64748b";
const GRID = "#1e293b";
const compact = new Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 2 });

const METRICS = {
  radius: "Radius (Earth radii)",
  mass: "Mass (Earth masses)",
  period: "Orbital period (days)",
};

const tooltipStyle = {
  contentStyle: { background: "#0f172a", border: "1px solid #334155", borderRadius: 8 },
  labelStyle: { color: "#e2e8f0" },
  itemStyle: { color: "#cbd5e1" },
  cursor: { fill: "rgba(148,163,184,0.08)" },
};

function ChartCard({ title, note, controls, state, children }) {
  return (
    <section className="rounded-xl border border-white/10 bg-slate-900/50 p-5 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h2 className="text-lg font-medium text-white">{title}</h2>
        {controls}
      </div>
      <div className="mt-4">
        {state.error && <ErrorBox error={state.error} onRetry={state.reload} />}
        {!state.error && !state.data && <Loading />}
        {!state.error && state.data && <div className="h-80">{children}</div>}
      </div>
      {note && <p className="mt-3 text-xs text-slate-500">{note}</p>}
    </section>
  );
}

function Distribution() {
  const [metric, setMetric] = useState("radius");
  const state = useFetch((signal) => api.histogram(metric, signal), [metric]);

  const data = (state.data ?? []).map((b) => ({
    range: `${compact.format(b.low)}–${compact.format(b.high)}`,
    count: b.count,
  }));

  const controls = (
    <div className="flex gap-2">
      {Object.keys(METRICS).map((key) => (
        <button
          key={key}
          onClick={() => setMetric(key)}
          className={`rounded-full border px-3 py-1 text-xs ${
            metric === key ? "border-sky-500 bg-sky-500/20 text-sky-200" : "border-slate-700 text-slate-400 hover:text-white"
          }`}
        >
          {key}
        </button>
      ))}
    </div>
  );

  return (
    <ChartCard
      title={`Distribution of ${metric}`}
      controls={controls}
      state={state}
      note="Bins are log-spaced, so each bar covers a factor of about 1.8 (radius), 3.2 (mass) or 10 (period). Planets with no value are not counted."
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
          <CartesianGrid stroke={GRID} vertical={false} />
          <XAxis
            dataKey="range" stroke={AXIS} interval={0} angle={-35} textAnchor="end" height={60}
            tick={{ fontSize: 11 }}
            label={{ value: METRICS[metric], position: "insideBottom", offset: -5, fill: "#94a3b8", fontSize: 12 }}
          />
          <YAxis stroke={AXIS} tickFormatter={(v) => compact.format(v)} />
          <Tooltip {...tooltipStyle} formatter={(v) => [v.toLocaleString(), "Planets"]} />
          <Bar dataKey="count" fill="#38bdf8" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

function PointTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950 p-3 text-xs text-slate-300">
      <div className="text-sm text-white">{p.name}</div>
      <div>{p.radius_earth.toLocaleString()} Earth radii</div>
      <div>{p.orbital_period_days.toLocaleString()} day orbit</div>
      <div style={{ color: CATEGORY_COLORS[p.category] }}>{p.category}</div>
      <div className="mt-1 text-slate-500">Click to open</div>
    </div>
  );
}

function RadiusVsPeriod() {
  const navigate = useNavigate();
  const state = useFetch((signal) => api.radiusPeriodPoints(signal), []);

  const groups = useMemo(() => {
    const result = Object.fromEntries(CATEGORY_ORDER.map((c) => [c, []]));
    (state.data ?? []).forEach((p) => result[p.category]?.push(p));
    return result;
  }, [state.data]);

  // Different Recharts versions pass the clicked point differently, so accept both shapes.
  function open(point) {
    const p = point?.payload ?? point;
    if (p?.name) navigate(`/planets/${encodeURIComponent(p.name)}`);
  }

  return (
    <ChartCard
      title="Planet size against orbit length"
      state={state}
      note="Both axes are logarithmic. Most known planets orbit close to their star, partly because the main detection methods find short orbits and large planets most easily. About 8 planets with periods over 100,000 days fall off the right edge."
    >
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 10 }}>
          <CartesianGrid stroke={GRID} />
          <XAxis
            type="number" dataKey="orbital_period_days" name="Orbital period" scale="log"
            domain={[0.1, 100000]} ticks={[0.1, 1, 10, 100, 1000, 10000, 100000]}
            allowDataOverflow tickFormatter={(v) => compact.format(v)} stroke={AXIS}
            label={{ value: "Orbital period (days)", position: "bottom", offset: 10, fill: "#94a3b8", fontSize: 12 }}
          />
          <YAxis
            type="number" dataKey="radius_earth" name="Radius" scale="log"
            domain={[0.2, 100]} ticks={[0.3, 1, 3, 10, 30, 100]} allowDataOverflow
            tickFormatter={(v) => compact.format(v)} stroke={AXIS}
            label={{ value: "Radius (Earth radii)", angle: -90, position: "insideLeft", fill: "#94a3b8", fontSize: 12 }}
          />
          <ZAxis range={[14, 14]} />
          <Tooltip content={<PointTooltip />} cursor={{ strokeDasharray: "3 3" }} />
          <Legend verticalAlign="top" height={30} />
          {CATEGORY_ORDER.filter((c) => groups[c].length > 0).map((c) => (
            <Scatter
              key={c} name={c} data={groups[c]} fill={CATEGORY_COLORS[c]} fillOpacity={0.55}
              isAnimationActive={false} onClick={open} style={{ cursor: "pointer" }}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

function Discoveries() {
  const state = useFetch((signal) => api.discoveriesPerYear(signal), []);

  return (
    <ChartCard
      title="Planets discovered per year"
      state={state}
      note="The tall bars in 2014 and 2016 most likely reflect large batches of Kepler candidates confirmed in those years, not a sudden jump in the sky."
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={state.data ?? []} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
          <CartesianGrid stroke={GRID} vertical={false} />
          <XAxis dataKey="year" stroke={AXIS} minTickGap={14} tick={{ fontSize: 11 }} />
          <YAxis stroke={AXIS} />
          <Tooltip {...tooltipStyle} formatter={(v) => [v.toLocaleString(), "Planets"]} />
          <Bar dataKey="count" fill="#a78bfa" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export default function Insights() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-white">Insights</h1>
      <Distribution />
      <RadiusVsPeriod />
      <Discoveries />
    </div>
  );
}