const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, options);
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError(0, "Cannot reach the server. Is the API running?");
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join("; ");
    } catch {
      // body was not JSON, keep the generic message
    }
    throw new ApiError(response.status, message);
  }
  return response.json();
}

// Builds "?a=1&b=2", skipping empty values.
function toQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

export const api = {
  statistics: (signal) => request("/statistics", { signal }),
  largestPlanet: (signal) => request("/planets/largest", { signal }),
  searchPlanets: (params, signal) => request(`/planets/search${toQuery(params)}`, { signal }),
  planet: (name, signal) => request(`/planets/${encodeURIComponent(name)}`, { signal }),
  comparePlanets: (names, signal) =>
    request("/planets/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ names }),
      signal,
    }),
  listStars: (params, signal) => request(`/stars${toQuery(params)}`, { signal }),
  star: (id, signal) => request(`/stars/${id}`, { signal }),
  histogram: (metric, signal) => request(`/insights/histogram?metric=${metric}`, { signal }),
  radiusPeriodPoints: (signal) => request("/insights/radius-period", { signal }),
  discoveriesPerYear: (signal) => request("/insights/discoveries", { signal }),
};