"use client";
import { useState, useEffect } from "react";
import {
  Activity, ChevronRight, Timer, Gauge, CircuitBoard,
  RotateCcw, Flag, Map, TrendingUp, Zap, Wind,
  Thermometer, CloudRain, Milestone, BarChart3
} from "lucide-react";
import {
  LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
  XAxis, YAxis, Tooltip, ResponsiveContainer, ZAxis, Cell
} from "recharts";

type TelemetryPoint = {
  Distance: number;
  Speed: number;
  Throttle: number;
  Brake: number;
  nGear: number;
  RPM: number;
  X: number;
  Y: number;
  Driver: string;
};

type CircuitInfo = {
  "Official Event Name": string;
  Location: string;
  Country: string;
  "Event Date": string;
  "Weekend Format": string;
};

const COMPOUNDS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"] as const;
const GRID = ["VER","HAM","ALO","LEC","SAI","NOR","PIA","RUS","PER","OCO","BOT","MAG","ALB","TSU","STR","ZHO","HUL","SAR"] as const;
const API_BASE = "http://localhost:8000";

function speedColor(speed: number): string {
  if (speed < 100) return "#0055FF";
  if (speed < 180) return "#00D2BE";
  if (speed < 260) return "#FFD700";
  return "#FF1801";
}

function fmt(n: number, d = 1): string { return n.toFixed(d); }

function StatsGrid({ data }: { data: TelemetryPoint[] }) {
  if (!data.length) return null;
  const speeds = data.map(d => d.Speed);
  const throttles = data.map(d => d.Throttle);
  const brakes = data.map(d => d.Brake);
  const maxS = Math.max(...speeds);
  const minS = Math.min(...speeds);
  const avgS = speeds.reduce((a, b) => a + b, 0) / speeds.length;
  const avgT = throttles.reduce((a, b) => a + b, 0) / throttles.length;
  const avgB = brakes.reduce((a, b) => a + b, 0) / brakes.length;

  const cells = [
    { label: "Max Speed", value: `${fmt(maxS, 0)}`, unit: "km/h", color: "var(--f1-red)" },
    { label: "Min Speed", value: `${fmt(minS, 0)}`, unit: "km/h", color: "var(--f1-blue)" },
    { label: "Avg Speed", value: `${fmt(avgS, 0)}`, unit: "km/h", color: "var(--f1-teal)" },
    { label: "Throttle", value: `${fmt(avgT, 1)}`, unit: "%", color: "var(--f1-teal)" },
    { label: "Brake", value: `${fmt(avgB, 1)}`, unit: "%", color: "var(--f1-red)" },
    { label: "Data Pts", value: `${data.length}`, unit: "", color: "var(--accent-silver)" },
  ];
  return (
    <div className="grid grid-cols-3 lg:grid-cols-6 gap-3">
      {cells.map((c, i) => (
        <div key={i} className={`glass-panel rounded-lg p-3 text-center animate-count-up stagger-${i + 1}`}>
          <p className="text-[9px] tracking-[0.2em] text-[var(--text-tertiary)] uppercase font-semibold">{c.label}</p>
          <p className="text-xl font-mono font-light mt-1" style={{ color: c.color }}>{c.value}</p>
          {c.unit && <p className="text-[10px] text-[var(--text-tertiary)]">{c.unit}</p>}
        </div>
      ))}
    </div>
  );
}

export default function F1Dashboard() {
  const [activeTab, setActiveTab] = useState("predict");
  const [year, setYear] = useState("2023");
  const [circuits, setCircuits] = useState<string[]>([]);
  const [circuit, setCircuit] = useState("");
  const [driver, setDriver] = useState("VER");

  const [tyreLife, setTyreLife] = useState(15);
  const [compound, setCompound] = useState("MEDIUM");
  const [predictedTime, setPredictedTime] = useState<number | null>(null);
  const [predictError, setPredictError] = useState<string | null>(null);
  const [predicting, setPredicting] = useState(false);

  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [telemetryError, setTelemetryError] = useState<string | null>(null);

  const [circuitInfo, setCircuitInfo] = useState<CircuitInfo | null>(null);
  const [trackData, setTrackData] = useState<TelemetryPoint[]>([]);
  const [circuitLoading, setCircuitLoading] = useState(false);
  const [circuitError, setCircuitError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/schedule/${year}`)
      .then(r => r.json())
      .then(d => { if (d.circuits?.length) { setCircuits(d.circuits); if (!circuit || !d.circuits.includes(circuit)) setCircuit(d.circuits[0]); } })
      .catch(() => {});
  }, [year]);

  const runPrediction = async () => {
    setPredictError(null); setPredictedTime(null); setPredicting(true);
    try {
      const res = await fetch(`${API_BASE}/predict_pace`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tyre_life: tyreLife, compound }),
      });
      const data = await res.json();
      if (!res.ok) { setPredictError(data.detail || "Prediction failed"); return; }
      await new Promise(r => setTimeout(r, 400));
      setPredictedTime(data.predicted_lap_time_seconds);
    } catch { setPredictError("API offline. Start the backend."); }
    finally { setPredicting(false); }
  };

  const fetchTelemetry = async () => {
    setLoading(true); setTelemetryError(null); setTelemetry([]);
    try {
      const res = await fetch(`${API_BASE}/telemetry/${year}/${circuit}/${driver}`);
      const data = await res.json();
      if (!res.ok) { setTelemetryError(data.detail || "Failed to fetch telemetry"); return; }
      setTelemetry(data);
    } catch { setTelemetryError("API offline. Start the backend."); }
    finally { setLoading(false); }
  };

  const fetchCircuitAnalytics = async () => {
    setCircuitLoading(true); setCircuitError(null); setCircuitInfo(null); setTrackData([]);
    try {
      const [infoRes, telemRes] = await Promise.all([
        fetch(`${API_BASE}/circuit_info/${year}/${circuit}`),
        fetch(`${API_BASE}/telemetry/${year}/${circuit}/${driver}`),
      ]);
      if (infoRes.ok) setCircuitInfo(await infoRes.json());
      else setCircuitError("Circuit info unavailable");
      if (telemRes.ok) setTrackData(await telemRes.json());
      else if (!circuitError) setCircuitError(prev => prev ? prev : "Telemetry unavailable");
    } catch { setCircuitError("API offline. Start the backend."); }
    finally { setCircuitLoading(false); }
  };

  return (
    <div className="flex h-screen w-full bg-[var(--bg-primary)] text-[var(--text-primary)] font-[var(--font-sans)] antialiased">

      {/* ═══════════ SIDEBAR ═══════════ */}
      <aside className="w-[240px] shrink-0 carbon-surface border-r border-[var(--border-subtle)] flex flex-col z-20 select-none">
        <div className="h-14 flex items-center gap-2.5 px-4 border-b border-[var(--border-subtle)]">
          <div className="w-7 h-7 rounded-full bg-[var(--f1-red)] flex items-center justify-center shadow-[0_0_18px_var(--f1-red-glow)]">
            <Gauge size={13} className="text-white" />
          </div>
          <div>
            <h1 className="text-xs font-bold tracking-[0.15em] text-white leading-tight">F1 INTELLIGENCE</h1>
            <p className="text-[9px] tracking-[0.2em] text-[var(--text-tertiary)] uppercase">Command Center</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-5 space-y-5">
          <div>
            <h2 className="text-[9px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase mb-3 font-semibold">Parameters</h2>
            <div className="space-y-4">
              <Field label="Season">
                <select value={year} onChange={e => setYear(e.target.value)}
                  className="w-full bg-black/40 border border-[var(--border-glass)] rounded px-3 py-2 text-xs text-[var(--text-primary)] focus:outline-none focus:border-[var(--border-active)] transition-colors">
                  {[2024,2023,2022,2021,2020,2019,2018].map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </Field>
              <Field label="Circuit">
                <select value={circuit} onChange={e => setCircuit(e.target.value)}
                  className="w-full bg-black/40 border border-[var(--border-glass)] rounded px-3 py-2 text-xs text-[var(--text-primary)] focus:outline-none focus:border-[var(--border-active)] transition-colors">
                  {circuits.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </Field>
              <Field label="Driver">
                <select value={driver} onChange={e => setDriver(e.target.value)}
                  className="w-full bg-black/40 border border-[var(--border-glass)] rounded px-3 py-2 text-xs text-[var(--text-primary)] focus:outline-none focus:border-[var(--border-active)] transition-colors">
                  {GRID.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </Field>
            </div>
          </div>

          <div className="pt-4 border-t border-[var(--border-subtle)] space-y-3">
            <div className="rounded bg-black/30 p-2.5 border border-[var(--border-subtle)]">
              <div className="flex items-center gap-1.5 text-[9px] tracking-[0.15em] text-[var(--text-tertiary)] uppercase mb-1">
                <RotateCcw size={9} /> Data Cache
              </div>
              <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">First fetch downloads data from F1 servers (~20s). Subsequent loads are instant.</p>
            </div>
            <div className="flex items-center gap-2 text-[9px] tracking-[0.15em] text-[var(--text-tertiary)]">
              <span className="status-dot status-dot--live" />
              System Online
            </div>
          </div>
        </div>
      </aside>

      {/* ═══════════ MAIN ═══════════ */}
      <div className="flex-1 flex flex-col h-screen min-w-0">

        {/* ── Telemetry Bar ── */}
        <div className="telem-bar h-11 flex items-center px-5 gap-5 z-10">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-mono font-bold text-[var(--f1-red)] tracking-wider">{driver}</span>
            <span className="w-px h-3 bg-[var(--border-glass)]" />
            <span className="text-[11px] text-[var(--text-secondary)] tracking-wide">{circuit || "—"}</span>
            <span className="w-px h-3 bg-[var(--border-glass)]" />
            <span className="text-[11px] text-[var(--text-tertiary)]">{year}</span>
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-2 text-[10px] text-[var(--text-tertiary)]">
            <span className="status-dot status-dot--live" />
            <span className="tracking-wider uppercase">Live</span>
          </div>
        </div>

        {/* ── Navigation ── */}
        <nav className="h-12 flex items-center gap-0.5 px-5 border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)] z-10">
          <TabBtn active={activeTab === "predict"} onClick={() => setActiveTab("predict")}>
            <Timer size={13} /> Pace Predictor
          </TabBtn>
          <TabBtn active={activeTab === "telemetry"} onClick={() => setActiveTab("telemetry")}>
            <Activity size={13} /> Telemetry
          </TabBtn>
          <TabBtn active={activeTab === "circuit"} onClick={() => setActiveTab("circuit")}>
            <Map size={13} /> Circuit Analytics
          </TabBtn>
        </nav>

        {/* ── Content ── */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-5 lg:p-7 max-w-6xl mx-auto">

            {/* ═══════════════ TAB: PREDICTOR ═══════════════ */}
            {activeTab === "predict" && (
              <div className="space-y-6 animate-slide-up">
                <header>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="badge"><Zap size={9} /> ML Engine</span>
                    <span className="text-[9px] text-[var(--text-tertiary)] tracking-wider">Random Forest Regressor</span>
                  </div>
                  <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">Pace Prediction</h2>
                  <p className="text-sm text-[var(--text-secondary)] mt-0.5">Lap time forecast based on tyre compound degradation model</p>
                </header>

                <div className="glass-panel rounded-xl p-6 lg:p-7 space-y-7 stagger-1 animate-slide-up">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <label className="text-[9px] tracking-[0.2em] text-[var(--text-tertiary)] uppercase font-semibold">Compound Selection</label>
                      <select value={compound} onChange={e => setCompound(e.target.value)}
                        className="w-full bg-black/40 border border-[var(--border-glass)] rounded-lg px-4 py-3 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--border-active)] transition-colors">
                        {COMPOUNDS.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </div>
                    <div className="space-y-3">
                      <label className="text-[9px] tracking-[0.2em] text-[var(--text-tertiary)] uppercase font-semibold">
                        Tyre Age — <span className="text-[var(--f1-red)] font-mono text-xs">{tyreLife}</span> laps
                      </label>
                      <input type="range" min={1} max={50} value={tyreLife} onChange={e => setTyreLife(parseInt(e.target.value))} className="w-full" />
                      <div className="flex justify-between text-[9px] text-[var(--text-tertiary)] tracking-wider">
                        <span>Fresh</span>
                        <span>High Degradation</span>
                      </div>
                    </div>
                  </div>

                  <button onClick={runPrediction} disabled={predicting}
                    className="btn-primary w-full rounded-lg py-3 flex items-center justify-center gap-2 text-xs disabled:opacity-50 disabled:cursor-not-allowed">
                    {predicting ? (
                      <span className="flex items-center gap-2"><span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Computing</span>
                    ) : (
                      <span className="flex items-center gap-2">Execute Simulation <ChevronRight size={15} /></span>
                    )}
                  </button>
                </div>

                {predictError && (
                  <div className="glass-panel rounded-xl p-4 border-l-2 border-[var(--f1-red)] stagger-2 animate-slide-up">
                    <p className="text-sm text-[var(--f1-red)]">{predictError}</p>
                  </div>
                )}

                {predictedTime !== null && (
                  <div className="glass-panel-glow rounded-xl p-6 lg:p-8 text-center stagger-3 animate-slide-up">
                    <p className="text-[9px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold mb-3">Estimated Lap Pace</p>
                    <div className="flex items-baseline justify-center gap-1.5">
                      <span className="stat-value text-5xl lg:text-7xl text-white tracking-tight">{predictedTime.toFixed(3)}</span>
                      <span className="text-base text-[var(--text-tertiary)] font-mono">s</span>
                    </div>
                    <div className="mt-4 h-1 bg-black/40 rounded-full overflow-hidden max-w-xs mx-auto">
                      <div className="h-full bg-[var(--f1-red)] rounded-full transition-all duration-1000 ease-out" style={{ width: `${Math.min((tyreLife / 50) * 100, 100)}%` }} />
                    </div>
                    <p className="text-[10px] text-[var(--text-tertiary)] mt-3 tracking-wide">
                      Degradation impact — {compound} · {tyreLife} laps
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* ═══════════════ TAB: TELEMETRY ═══════════════ */}
            {activeTab === "telemetry" && (
              <div className="space-y-6 animate-slide-up">
                <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                  <header>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="badge"><BarChart3 size={9} /> High-Resolution</span>
                      <span className="text-[9px] text-[var(--text-tertiary)] tracking-wider">10 Hz Telemetry</span>
                    </div>
                    <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">Grid Telemetry</h2>
                    <p className="text-sm text-[var(--text-secondary)] mt-0.5 tracking-wide">
                      <span className="font-mono text-[var(--f1-red)]">{driver}</span> · {circuit} · {year}
                    </p>
                  </header>
                  <button onClick={fetchTelemetry} disabled={loading}
                    className="btn-secondary rounded-lg px-5 py-2.5 text-xs flex items-center gap-2 shrink-0 disabled:opacity-50 disabled:cursor-not-allowed">
                    {loading ? (
                      <span className="flex items-center gap-2"><span className="w-3 h-3 border-2 border-[var(--text-secondary)]/30 border-t-[var(--text-secondary)] rounded-full animate-spin" /> Querying</span>
                    ) : (
                      <span className="flex items-center gap-2"><CircuitBoard size={13} /> Fetch Telemetry</span>
                    )}
                  </button>
                </div>

                {telemetryError && (
                  <div className="glass-panel rounded-xl p-4 border-l-2 border-[var(--f1-red)]">
                    <p className="text-sm text-[var(--f1-red)]">{telemetryError}</p>
                  </div>
                )}

                {telemetry.length > 0 ? (
                  <div className="space-y-5">
                    <StatsGrid data={telemetry} />
                    <div className="grid grid-rows-2 gap-5 min-h-[480px]">
                      <div className="glass-panel rounded-xl p-5 relative stagger-1 animate-slide-up">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-[9px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold">Speed <span className="text-[var(--text-muted)]">(km/h)</span></h3>
                          <span className="text-[9px] text-[var(--text-tertiary)] font-mono">MAX {telemetry.length ? fmt(Math.max(...telemetry.map(d => d.Speed)), 0) : '—'}</span>
                        </div>
                        <div className="h-[calc(100%-32px)]">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={telemetry} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
                              <XAxis dataKey="Distance" hide />
                              <YAxis domain={["minData", "maxData"]} hide />
                              <Tooltip contentStyle={{ background: "#0a0a0a", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px", fontSize: "12px", boxShadow: "0 8px 24px rgba(0,0,0,0.6)" }} labelStyle={{ color: "#888" }} />
                              <Line type="monotone" dataKey="Speed" stroke="var(--f1-red)" strokeWidth={2} dot={false} activeDot={{ r: 3, fill: "var(--f1-red)", strokeWidth: 0 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                      <div className="glass-panel rounded-xl p-5 relative stagger-2 animate-slide-up">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-[9px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold">Throttle <span className="text-[var(--text-muted)]">(%)</span></h3>
                          <span className="text-[9px] text-[var(--text-tertiary)] font-mono">AVG {telemetry.length ? fmt(telemetry.reduce((a, d) => a + d.Throttle, 0) / telemetry.length, 1) : '—'}%</span>
                        </div>
                        <div className="h-[calc(100%-32px)]">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={telemetry} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
                              <XAxis dataKey="Distance" hide />
                              <YAxis domain={[0, 100]} hide />
                              <Tooltip contentStyle={{ background: "#0a0a0a", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px", fontSize: "12px", boxShadow: "0 8px 24px rgba(0,0,0,0.6)" }} labelStyle={{ color: "#888" }} />
                              <Area type="step" dataKey="Throttle" stroke="#00D2BE" fill="#00D2BE" fillOpacity={0.12} strokeWidth={2} activeDot={{ r: 3, fill: "#00D2BE", strokeWidth: 0 }} />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  !telemetryError && (
                    <div className="glass-panel rounded-xl flex items-center justify-center h-[400px] border border-dashed border-[var(--border-glass)] stagger-1 animate-fade-in">
                      <div className="text-center">
                        <Activity size={28} className="mx-auto text-[var(--text-muted)] mb-3" />
                        <p className="text-sm text-[var(--text-tertiary)] tracking-widest uppercase">Awaiting Query</p>
                        <p className="text-[10px] text-[var(--text-muted)] mt-1">Select parameters and fetch telemetry data</p>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}

            {/* ═══════════════ TAB: CIRCUIT ANALYTICS ═══════════════ */}
            {activeTab === "circuit" && (
              <div className="space-y-6 animate-slide-up">
                <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                  <header>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="badge"><Flag size={9} /> Track Analysis</span>
                      <span className="text-[9px] text-[var(--text-tertiary)] tracking-wider">{driver} · Fastest Lap</span>
                    </div>
                    <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">Circuit Analytics</h2>
                    <p className="text-sm text-[var(--text-secondary)] mt-0.5 tracking-wide">{circuit} — {year} Season</p>
                  </header>
                  <button onClick={fetchCircuitAnalytics} disabled={circuitLoading}
                    className={`btn-secondary rounded-lg px-5 py-2.5 text-xs flex items-center gap-2 shrink-0 disabled:opacity-50 disabled:cursor-not-allowed ${circuitLoading ? 'cursor-wait' : ''}`}>
                    {circuitLoading ? (
                      <span className="flex items-center gap-2"><span className="w-3 h-3 border-2 border-[var(--text-secondary)]/30 border-t-[var(--text-secondary)] rounded-full animate-spin" /> Loading Track</span>
                    ) : (
                      <span className="flex items-center gap-2"><Map size={13} /> Analyze Circuit</span>
                    )}
                  </button>
                </div>

                {circuitError && (
                  <div className="glass-panel rounded-xl p-4 border-l-2 border-[var(--f1-red)]">
                    <p className="text-sm text-[var(--f1-red)]">{circuitError}</p>
                  </div>
                )}

                {(circuitInfo || trackData.length > 0) && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                    {/* Circuit Info Panel */}
                    {circuitInfo && (
                      <div className="glass-panel rounded-xl p-5 space-y-4 stagger-1 animate-slide-up lg:col-span-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Flag size={14} className="text-[var(--f1-red)]" />
                          <h3 className="text-[10px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold">Event Data</h3>
                        </div>
                        <div className="space-y-3">
                          {[
                            { label: "Official Name", value: circuitInfo["Official Event Name"] },
                            { label: "Location", value: circuitInfo.Location },
                            { label: "Country", value: circuitInfo.Country },
                            { label: "Date", value: circuitInfo["Event Date"] },
                            { label: "Format", value: circuitInfo["Weekend Format"] },
                          ].map((row, i) => (
                            <div key={i} className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-2 last:border-0 last:pb-0">
                              <span className="text-[10px] tracking-[0.1em] text-[var(--text-tertiary)] uppercase">{row.label}</span>
                              <span className="text-xs text-[var(--text-primary)] font-medium">{row.value}</span>
                            </div>
                          ))}
                        </div>

                        <div className="pt-3 border-t border-[var(--border-subtle)]">
                          <div className="flex items-center gap-2 text-[9px] tracking-[0.15em] text-[var(--text-tertiary)] uppercase">
                            <CloudRain size={10} />
                            Weather Data
                          </div>
                          <p className="text-[10px] text-[var(--text-secondary)] mt-1">Historical weather available via API endpoint</p>
                        </div>
                      </div>
                    )}

                    {/* GPS Track Map */}
                    <div className={`glass-panel rounded-xl p-5 ${circuitInfo ? 'lg:col-span-2' : 'lg:col-span-3'} stagger-2 animate-slide-up`}>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-[10px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold">
                          GPS Track Layout — Speed Heatmap
                        </h3>
                        <div className="flex items-center gap-3 text-[9px] text-[var(--text-tertiary)]">
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#0055FF" }} /> Low</span>
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#00D2BE" }} /> Med</span>
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#FFD700" }} /> High</span>
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: "#FF1801" }} /> Peak</span>
                        </div>
                      </div>
                      {trackData.length > 0 ? (
                        <div className="h-[400px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                              <XAxis dataKey="X" type="number" domain={["minData", "maxData"]} hide />
                              <YAxis dataKey="Y" type="number" domain={["minData", "maxData"]} hide />
                              <ZAxis range={[0, 0]} />
                              <Tooltip
                                contentStyle={{ background: "#0a0a0a", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px", fontSize: "12px", boxShadow: "0 8px 24px rgba(0,0,0,0.6)" }}
                                formatter={(value, name) => [name === "Speed" ? `${fmt(value as number, 0)} km/h` : fmt(value as number, 0), name] as [string, string]}
                                labelFormatter={() => ""}
                              />
                              <Scatter data={trackData} line={{ stroke: "rgba(255,255,255,0.05)", strokeWidth: 1 }} lineType="joint" shape="circle" fill="var(--f1-red)" legendType="none">
                                {trackData.map((entry, i) => (
                                  <Cell key={i} fill={speedColor(entry.Speed)} />
                                ))}
                              </Scatter>
                            </ScatterChart>
                          </ResponsiveContainer>
                        </div>
                      ) : (
                        <div className="h-[400px] flex items-center justify-center border border-dashed border-[var(--border-glass)] rounded-lg">
                          <div className="text-center">
                            <Map size={28} className="mx-auto text-[var(--text-muted)] mb-2" />
                            <p className="text-xs text-[var(--text-tertiary)] tracking-wider">No track data loaded</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Telemetry Stats */}
                {trackData.length > 0 && (
                  <div className="stagger-3 animate-slide-up">
                    <div className="flex items-center gap-2 mb-4">
                      <TrendingUp size={13} className="text-[var(--text-tertiary)]" />
                      <h3 className="text-[10px] tracking-[0.25em] text-[var(--text-tertiary)] uppercase font-semibold">Lap Statistics</h3>
                    </div>
                    <StatsGrid data={trackData} />
                  </div>
                )}

                {/* Empty state */}
                {!circuitInfo && !trackData.length && !circuitError && (
                  <div className="glass-panel rounded-xl flex items-center justify-center h-[400px] border border-dashed border-[var(--border-glass)] stagger-1 animate-fade-in">
                    <div className="text-center">
                      <Milestone size={28} className="mx-auto text-[var(--text-muted)] mb-3" />
                      <p className="text-sm text-[var(--text-tertiary)] tracking-widest uppercase">Circuit Analysis</p>
                      <p className="text-[10px] text-[var(--text-muted)] mt-1">Load circuit data to view GPS track layout and event information</p>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-[9px] tracking-[0.2em] text-[var(--text-tertiary)] uppercase font-semibold block">{label}</label>
      {children}
    </div>
  );
}

function TabBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick}
      className={`relative flex items-center gap-1.5 px-3.5 py-1.5 text-[10px] tracking-[0.15em] uppercase font-semibold rounded-md transition-all duration-300 ${
        active
          ? "text-white bg-white/[0.05] border border-[var(--border-glass-hover)] shadow-sm"
          : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-white/[0.015]"
      }`}>
      {active && <span className="absolute inset-0 rounded-md border border-[var(--f1-red)]/30 animate-glow-pulse pointer-events-none" />}
      {children}
    </button>
  );
}
