import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "./api";
import { useFetch } from "./useFetch";
import { CATEGORY_COLORS } from "./utils";

const STAR_TINTS = ["255,255,255", "186,214,255", "255,236,200"];

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

// Colour of a star from its surface temperature in kelvin (rough, for display only).
function starColor(teff) {
  if (teff == null) return "#ffd27a";
  if (teff < 3500) return "#ff7a45";
  if (teff < 5000) return "#ffb34d";
  if (teff < 6000) return "#ffe08a";
  if (teff < 7500) return "#fff4d6";
  return "#cfe2ff";
}

export function CountUp({ value }) {
  const [count, setCount] = useState(0);
  const reduce = prefersReducedMotion();

  useEffect(() => {
    const target = Number(value);
    if (!Number.isFinite(target)) return;
    if (reduce) return;

    const start = performance.now();
    let frame = 0;
    function update(now) {
      const progress = Math.min((now - start) / 1000, 1);
      setCount(Math.round(target * (1 - (1 - progress) ** 3)));
      if (progress < 1) frame = requestAnimationFrame(update);
    }

    frame = requestAnimationFrame(update);
    return () => cancelAnimationFrame(frame);
  }, [value, reduce]);

  return <>{(reduce ? Number(value) : count).toLocaleString()}</>;
}

export function Globe({ color, size }) {
  return (
    <div
      aria-hidden="true"
      className="globe-surface relative shrink-0 overflow-hidden rounded-full"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle at 32% 28%, #ffffff 0%, ${color} 28%, ${color}bb 58%, #08101f 100%)`,
        boxShadow: `inset -12px -8px 18px #020617aa, 0 0 26px ${color}66`,
      }}
    >
      <span
        className="absolute inset-0"
        style={{ backgroundImage: "repeating-linear-gradient(0deg, transparent 0 14px, rgba(255,255,255,0.12) 15px 17px)" }}
      />
    </div>
  );
}

// ---------- Background: twinkling, drifting stars and shooting stars ----------

export function StarField() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const reduce = prefersReducedMotion();

    let width = 0;
    let height = 0;
    let stars = [];
    let meteors = [];
    let nextMeteor = 2500;
    let last = performance.now();
    let raf = 0;

    function resize() {
      const dpr = window.devicePixelRatio || 1;
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const count = Math.min(280, Math.floor((width * height) / 7000));
      stars = Array.from({ length: count }, () => {
        const depth = Math.random() ** 2; // most stars are far away (small and faint)
        return {
          x: Math.random() * width,
          y: Math.random() * height,
          depth,
          r: 0.3 + depth * 1.3,
          speed: 0.03 + depth * 0.15,
          twinkle: 0.6 + Math.random() * 1.8,
          phase: Math.random() * Math.PI * 2,
          tint: STAR_TINTS[Math.floor(Math.random() * STAR_TINTS.length)],
        };
      });
      if (reduce) draw(0, 0); // a still sky: draw once
    }

    function draw(time, dt) {
      ctx.clearRect(0, 0, width, height);

      for (const s of stars) {
        const twinkle = reduce ? 1 : 0.65 + 0.35 * Math.sin((time / 1000) * s.twinkle + s.phase);
        ctx.fillStyle = `rgba(${s.tint},${(0.3 + 0.7 * s.depth) * twinkle})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();

        if (!reduce) {
          s.x -= s.speed * dt;
          s.y += s.speed * 0.35 * dt;
          if (s.x < -2) s.x = width + 2;
          if (s.y > height + 2) s.y = -2;
        }
      }

      if (reduce) return;

      if (time > nextMeteor) {
        meteors.push({
          x: width * (0.35 + Math.random() * 0.65),
          y: Math.random() * height * 0.45,
          vx: -(7 + Math.random() * 5),
          vy: 3 + Math.random() * 2.5,
          life: 0,
          maxLife: 55 + Math.random() * 25,
        });
        nextMeteor = time + 3500 + Math.random() * 7000;
      }

      meteors = meteors.filter((m) => m.life < m.maxLife);
      for (const m of meteors) {
        m.x += m.vx * dt;
        m.y += m.vy * dt;
        m.life += dt;
        const fade = Math.sin((m.life / m.maxLife) * Math.PI); // fades in, then out
        const tailX = m.x - m.vx * 9;
        const tailY = m.y - m.vy * 9;
        const gradient = ctx.createLinearGradient(m.x, m.y, tailX, tailY);
        gradient.addColorStop(0, `rgba(255,255,255,${0.9 * fade})`);
        gradient.addColorStop(1, "rgba(255,255,255,0)");
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 1.6;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(m.x, m.y);
        ctx.lineTo(tailX, tailY);
        ctx.stroke();
      }
    }

    function loop(time) {
      const dt = Math.min(3, (time - last) / 16.67); // keeps speed the same on 60 Hz and 144 Hz screens
      last = time;
      draw(time, dt);
      raf = requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener("resize", resize);
    if (!reduce) raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 h-full w-full" />;
}

// ---------- Hero: a real planetary system, animated ----------

export function OrbitSystem({ hostname = "TRAPPIST-1" }) {
  const { data, error } = useFetch((signal) => api.searchPlanets({ hostname, limit: 12 }, signal), [hostname]);

  if (error) return null;
  if (!data) {
    return <div className="mx-auto aspect-square animate-pulse rounded-full border border-white/10" style={{ width: "min(86vw, 440px)" }} />;
  }
  if (data.items.length === 0) return null;

  // Innermost planet first. Rings are evenly spaced (schematic); speeds use real orbital periods.
  const planets = [...data.items].sort((a, b) => (a.semi_major_axis_au ?? 99) - (b.semi_major_axis_au ?? 99));
  const star = planets[0].star;
  const color = starColor(star?.temperature_k);
  const lightYears = star?.distance_pc ? Math.round(star.distance_pc * 3.2616) : null;

  return (
    <div>
      <div className="orbit-system relative mx-auto aspect-square" style={{ width: "min(86vw, 440px)" }}>
        <div
          className="sun absolute rounded-full"
          style={{
            width: "13%", height: "13%", top: "43.5%", left: "43.5%",
            background: `radial-gradient(circle at 35% 35%, #ffffff, ${color} 55%, ${color}aa)`,
            boxShadow: `0 0 40px 12px ${color}88, 0 0 120px 40px ${color}33`,
          }}
        />

        {planets.map((p, i) => {
          const diameter = 26 + (70 * (i + 1)) / planets.length; // % of the box
          const duration = Math.max(5, (p.orbital_period_days ?? 20) * 4); // seconds
          const delay = (i * 37) % duration;
          const size = Math.max(4, Math.min(12, 4 + (p.radius_earth ?? 1) * 1.5));

          return (
            <div
              key={p.planet_id ?? `${p.hostname}-${i}`}
              className="orbit absolute rounded-full border border-white/15"
              style={{
                width: `${diameter}%`,
                height: `${diameter}%`,
                top: `${(100 - diameter) / 2}%`,
                left: `${(100 - diameter) / 2}%`,
                animationDuration: `${duration}s`,
                animationDelay: `-${delay}s`,
              }}
            >
              <Link
                to={`/planets/${encodeURIComponent(p.name)}`}
                aria-label={p.name}
                title={p.name}
                className="absolute left-1/2 top-0 block -translate-x-1/2 -translate-y-1/2 rounded-full"
                style={{ width: size, height: size, backgroundColor: CATEGORY_COLORS[p.category] ?? CATEGORY_COLORS.Unknown }}
              />
            </div>
          );
        })}
      </div>
      {lightYears != null && (
        <p className="mt-4 text-center text-sm text-white/60">
          {hostname} · {lightYears.toLocaleString()} light-years away
        </p>
      )}
    </div>
  );
}