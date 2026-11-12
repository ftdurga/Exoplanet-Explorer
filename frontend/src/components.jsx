import { CATEGORY_COLORS, orbSize } from "./utils";

export const inputClass =
  "rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-sky-500 focus:outline-none";
export const buttonClass =
  "rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50";
export const ghostButtonClass =
  "rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50";

export function CategoryBadge({ category }) {
  const color = CATEGORY_COLORS[category] ?? CATEGORY_COLORS.Unknown;
  return (
    <span
      className="inline-block rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{ color, borderColor: color, backgroundColor: `${color}22` }}
    >
      {category}
    </span>
  );
}

// A planet drawn as a circle. Size comes from the radius, colour from the category.
export function Orb({ radius, category }) {
  const color = CATEGORY_COLORS[category] ?? CATEGORY_COLORS.Unknown;
  const px = orbSize(radius);
  return (
    <div
      className="shrink-0 rounded-full"
      style={{
        width: px,
        height: px,
        opacity: radius === null || radius === undefined ? 0.4 : 1,
        background: `radial-gradient(circle at 30% 30%, ${color}, ${color}66 65%, #0f172a)`,
      }}
      title={radius === null || radius === undefined ? "Radius unknown" : `${radius} Earth radii`}
    />
  );
}

export function Loading() {
  return (
    <div className="animate-pulse space-y-3" aria-label="Loading">
      <div className="h-6 w-1/3 rounded bg-slate-800" />
      <div className="h-24 rounded bg-slate-800" />
      <div className="h-24 rounded bg-slate-800" />
    </div>
  );
}

export function ErrorBox({ error, onRetry }) {
  return (
    <div role="alert" className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-red-200">
      <p className="font-medium">Something went wrong</p>
      <p className="mt-1 text-sm">{error.message}</p>
      {onRetry && (
        <button className={`${ghostButtonClass} mt-3`} onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ children }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-700 p-8 text-center text-slate-400">
      {children}
    </div>
  );
}

export function Pagination({ page, pageCount, total, onPage, loading }) {
  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
      <span>{total.toLocaleString()} results</span>
      <div className="flex items-center gap-3">
        <button className={ghostButtonClass} disabled={page <= 1 || loading} onClick={() => onPage(page - 1)}>
          Previous
        </button>
        <span>
          Page {page} of {pageCount}
        </span>
        <button className={ghostButtonClass} disabled={page >= pageCount || loading} onClick={() => onPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}

export function Fact({ label, note, children }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-lg text-slate-100">{children}</div>
      {note && <div className="mt-1 text-xs text-slate-500">{note}</div>}
    </div>
  );
}