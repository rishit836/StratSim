<div align="center">

# 📊 StratSim
<b>Django-based quantitative market data explorer, indicator engine & strategy playground.</b><br/>
<sub>Featuring multi‑timeframe price data, real‑time indicator computation, a composite Bullish ↔ Bearish sentiment gauge, and extensible strategy hooks.</sub>

---

### ⚡ Live Focus
Caching + threaded indicator computation + sentiment visualization (Zerodha‑style bar) + expanding strategy primitives.

</div>

---

## 🧠 Overview
StratSim is the experimental layer underneath the broader WalletTree vision. It lets me:
1. Pull & cache multi‑horizon OHLCV data (1D, 5D, 1M, 1Y, MAX)
2. Compute technical indicators concurrently (SMA, EMA, RSI, MACD, composite score)
3. Visualize everything with an interactive Chart.js board & toggleable legend
4. Produce a normalized 0 → 100 <em>bearishness</em> score (inverted for bullishness) shown via a gradient sentiment bar
5. Prepare the backbone for pluggable trading & backtest logic

---

## 🛠 Tech Stack
| Layer | Stack |
|-------|-------|
| Backend | Django, Python 3.x |
| Data | yfinance (historical + intraday), Polygon (intraday endpoint scaffolding) |
| Indicators | pandas, numpy (threaded computation) |
| Frontend | Django templates, Chart.js (dynamic multi‑dataset), custom CSS |
| Caching | Django cache (in‑memory/file depending on env) |
| Env | python-dotenv for API keys (e.g. `polygon_api`) |

---

## ✅ Implemented Features
| Domain | Feature |
|--------|---------|
| Data | Multi-period fetch: 1d, 5d, 1mo, 1y, max (cached) |
| Indicators | SMA(20), EMA(20), RSI(14), MACD (12/26/9), MACD histogram |
| Sentiment | Composite Bullish/Bearish score (0=strong bullish, 100=strong bearish) |
| Visualization | Chart.js with gradient close price, toggleable indicator legend, dynamic MACD secondary axis, auto-color MACD histogram bars |
| UI/UX | Zerodha‑style sentiment bar showing Bullish / Bearish split |
| Performance | Threaded indicator computation to reduce latency (`compute_indicators`) |
| Architecture | Background threaded multi‑timeframe prefetch & cache seeding |
| Resilience | Safe fallbacks when data insufficient (neutral score) |

---

## � Composite Bearishness Model
The score blends five normalized components (weights tunable):
1. Price vs EMA(20 / 50)
2. EMA(20) slope regression
3. RSI inversion (30 → bearish extreme)
4. MACD histogram (z‑scored within recent window)
5. Short-term structure (higher highs / lower lows heuristic)

Returns: `float` in `[0,100]` stored as `bearish_score` (and `bullish_score = 100 - bearish_score`).

---

## 🧩 Architecture Snapshot
```
┌────────────┐   fetch/cache   ┌────────────────┐   threaded calc   ┌────────────────────┐
│  yfinance   │ ─────────────▶ │   Data Frames   │ ───────────────▶ │ Indicator Engine   │
└────────────┘                 │ (multi-period)  │                  │ (SMA/EMA/RSI/MACD) │
	  ▲                       └───────┬─────────┘                  └─────────┬──────────┘
	  │ polygon (opt)                │ composite score calc                  │
	  │                               ▼                                      ▼
	  │                        ┌────────────────┐                     ┌─────────────────┐
	  │                        │ Django Cache   │◀────────────────────│  Sentiment Bar  │
	  │                        └──────┬─────────┘                     └────────┬────────┘
	  ▼                               │  JSON / AJAX response                   │ DOM update
  .env API key                         ▼                                        ▼
							Chart Data     ───────────▶   Chart.js Line / Bar Overlay
```

---

## 🖥 UI Elements
| Component | Description |
|-----------|-------------|
| Timeframe buttons | Switch active dataset (updates via cached key) |
| Legend pills | Toggle per-dataset visibility (close, indicators) |
| Sentiment bar | Gradient (green→amber→red) with floating marker & live value |
| MACD panel overlay | Uses secondary y‑axis & mixed line/bar datasets |

---

## � Getting Started
### 1. Clone
```bash
git clone https://github.com/rishit836/StratSim.git
cd StratSim
```
### 2. (Recommended) Virtual Env
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```
### 3. Install Dependencies *(create `requirements.txt` if not present)*
```bash
pip install django pandas numpy yfinance requests python-dotenv chartjs
```
> If you add a curated `requirements.txt`, replace the above with `pip install -r requirements.txt`.

### 4. Environment
Create a `.env` file:
```
polygon_api=YOUR_POLYGON_KEY
```

### 5. Run Server
```bash
python manage.py migrate
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

---

## 📦 Key Modules
| File | Purpose |
|------|---------|
| `walletTree/indicators.py` | Indicator + composite bearish score engine (threaded) |
| `walletTree/views.py` | Data collection, caching, JSON chart endpoint |
| `stocks/templates/loading.html` | Main interactive chart + legend + sentiment bar |
| `walletTree/bg_operations.py` | Background operation scaffolding |

---

## 🧪 Planned Additions
- Strategy plug-in interface (python class registry)
- Trade execution simulator (fills, slippage, pnl attribution)
- Equity curve + drawdown panels
- Risk metrics (Sharpe, Sortino, Max DD, Win Rate)
- Persistent portfolio & user auth flows
- Alternative data (sector classification, fundamentals)

---

## 🛣 Roadmap (High-Level)
| Status | Milestone |
|--------|-----------|
| ✅ | Core indicator engine + sentiment gauge |
| ✅ | Multi-period caching & rendering |
| 🚧 | Strategy API abstraction |
| ⏳ | Backtest runner + performance analytics |
| ⏳ | Portfolio persistence & multi-user support |
| ⏳ | AI-assisted strategy suggestions |

---

## 🧵 Concurrency Notes
Indicators are computed in parallel threads (Python `threading`) to reduce initial page load latency. This is safe here because operations are CPU‑light (pandas vector ops releasing GIL selectively). For heavier math consider `multiprocessing` or numba.

---

## 🔐 Disclaimer
Educational / experimental only. Not investment advice. Historical performance ≠ future returns.

---

## 🤝 Contributions
Currently a personal sandbox, but suggestions / issues welcome via GitHub issues.

---

## � Contact
Feel free to reach out or open an issue with improvement ideas around quant features or visualization polish.

---

<div align="center">
Made with 🧪, 📊 and ☕
</div>

