# F1 Intelligence Hub — Frontend

Next.js 16 dashboard for the F1 Intelligence platform. Three-tab race engineering interface with telemetry visualization, ML pace prediction, and circuit analytics.

## Quick Start

```bash
npm install
npm run dev
```

Requires the FastAPI backend running on `http://localhost:8000`.

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Start development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint check |

## Design System

The UI uses a custom F1-inspired design system defined in `app/globals.css`:

- **Carbon fiber** texture surfaces (`.carbon-surface`)
- **Glassmorphism** panels with blur and glow states (`.glass-panel`, `.glass-panel-glow`)
- **Telemetry bar** — fixed top strip with live status indicator
- **Speed heatmap** — per-point color mapping: blue → teal → yellow → red
- **Staggered animations** — `stagger-1` through `stagger-8` with `animate-slide-up`

Key CSS variables: `--f1-red: #FF1801`, `--bg-primary: #050505`, `--surface-glass`.

## Tabs

| Tab | Features |
|---|---|
| **Pace Predictor** | Compound selector, tyre life slider, ML prediction with glow result card |
| **Telemetry** | Speed line chart, throttle area chart, 6-metric stats grid |
| **Circuit Analytics** | GPS track map (X/Y scatter with speed heatmap), event info panel, lap statistics |

## Dependencies

- `next@16`, `react@19`, `react-dom@19`
- `recharts` — charting
- `lucide-react` — icons
- `tailwindcss@4`, `@tailwindcss/postcss` — styling
