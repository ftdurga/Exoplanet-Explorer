import { BrowserRouter, Link, NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Planets from "./pages/Planets";
import PlanetDetail from "./pages/PlanetDetail";
import StarDetail from "./pages/StarDetail";
import Compare from "./pages/Compare";
import { StarField } from "./space";
import Insights from "./pages/Insights";

const navClass = ({ isActive }) =>
  `rounded-md px-3 py-1.5 text-sm ${isActive ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"}`;

function NotFound() {
  return (
    <div className="py-16 text-center">
      <h1 className="text-2xl text-white">Page not found</h1>
      <Link to="/" className="mt-4 inline-block text-sky-400 hover:underline">
        Back to the dashboard
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
    <StarField />
      <div
        className="relative z-10 min-h-screen text-slate-200"
 
      >
        <header className="border-b border-slate-800">
          <nav className="mx-auto flex max-w-6xl items-center gap-2 px-4 py-3">
            <Link to="/" className="mr-4 text-lg font-semibold text-white">
              Exoplanet Explorer
            </Link>
            <NavLink to="/" end className={navClass}>Dashboard</NavLink>
            <NavLink to="/planets" className={navClass}>Planets</NavLink>
            <NavLink to="/compare" className={navClass}>Compare</NavLink>
            <NavLink to="/insights" className={navClass}>Insights</NavLink>
          </nav>
        </header>

        <main className="mx-auto max-w-6xl px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/planets" element={<Planets />} />
            <Route path="/planets/:name" element={<PlanetDetail />} />
            <Route path="/stars/:id" element={<StarDetail />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        <footer className="mx-auto max-w-6xl px-4 py-8 text-xs text-slate-600">
          Data: NASA Exoplanet Archive. Planet visuals are drawings scaled from the data, not photographs.
        </footer>
      </div>
    </BrowserRouter>
  );
}