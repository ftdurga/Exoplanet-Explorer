export const CATEGORY_ORDER = ["Earth-like", "Super-Earth", "Neptune-like", "Giant", "Unknown"];

export const CATEGORY_COLORS = {
  "Earth-like": "#34d399",
  "Super-Earth": "#2dd4bf",
  "Neptune-like": "#60a5fa",
  Giant: "#fb923c",
  Unknown: "#94a3b8",
};

export const MASS_NOTES = {
  Mass: "Measured mass",
  Msini: "Minimum mass (the true mass is higher)",
  "M-R relationship": "Estimated from radius, not measured",
};

// Number formatting that shows an em dash for missing values (null from the API).
export function fmt(value, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

// Circle diameter in pixels. Log scale, because radii range from 0.3 to 87 Earth radii.
export function orbSize(radiusEarth) {
  if (radiusEarth === null || radiusEarth === undefined) return 24;
  return Math.round(20 * (1 + Math.log2(1 + radiusEarth)));
}