import { AlertTriangle, LayoutDashboard, Microscope, Route, Settings2 } from "lucide-react";
import { NavLink, Route as RouterRoute, Routes } from "react-router-dom";

import { Header } from "./components/Header";
import { NotFoundPage } from "./pages/NotFoundPage";
import { Dashboard } from "./pages/Dashboard";
import { FlightDetail } from "./pages/FlightDetail";
import { ScenarioLab } from "./pages/ScenarioLab";
import { ImpactPage } from "./pages/ImpactPage";
import { ArchitecturePage } from "./pages/ArchitecturePage";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/scenario-lab", label: "Scenario Lab", icon: Settings2 },
  { to: "/impact", label: "Impact", icon: AlertTriangle },
  { to: "/architecture", label: "Architecture", icon: Microscope },
];

export default function App() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(84,209,219,0.12),_transparent_32%),linear-gradient(180deg,_#07111d_0%,_#09131f_48%,_#0c1520_100%)] text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 pb-6 pt-4 md:px-6">
        <Header />
        <div className="mt-4 grid flex-1 gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
          <aside className="hidden rounded-3xl border border-panelEdge/90 bg-panel/80 p-4 shadow-panel backdrop-blur lg:block">
            <div className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">
              <Route className="h-4 w-4 text-signal.cyan" />
              Navigation
            </div>
            <nav className="space-y-2">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    [
                      "flex items-center gap-3 rounded-2xl border px-3 py-3 text-sm transition",
                      isActive
                        ? "border-signal.cyan/40 bg-signal.cyan/10 text-white"
                        : "border-transparent bg-slate-950/30 text-slate-300 hover:border-panelEdge hover:bg-slate-900/60",
                    ].join(" ")
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </aside>
          <main className="min-w-0">
            <Routes>
              <RouterRoute path="/" element={<Dashboard />} />
              <RouterRoute path="/flight/:flightId" element={<FlightDetail />} />
              <RouterRoute path="/scenario-lab" element={<ScenarioLab />} />
              <RouterRoute path="/impact" element={<ImpactPage />} />
              <RouterRoute path="/architecture" element={<ArchitecturePage />} />
              <RouterRoute path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
        <footer className="mt-5 rounded-2xl border border-panelEdge/70 bg-slate-950/45 px-4 py-3 text-xs text-slate-400">
          Research demonstrator using synthetic but operationally grounded local decision-support simulation.
        </footer>
      </div>
    </div>
  );
}
