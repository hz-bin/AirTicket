# CTrip Flight Scraper - AI Agent Instructions

## Project Overview

This is a **dual-language flight price monitoring system** for CTrip (携程) that combines:
- **Python scraper** (`query.py`) - Selenium-based web scraper for direct flights
- **Go scheduler** (`AirTicket.go`) - Background service that runs queries 3x daily with randomized timing

Output: JSON + multi-sheet Excel files (`flights_history.xlsx`), one sheet per flight tracking price history.

## Architecture & Data Flow

```
config.json → AirTicket.exe (Go scheduler)
                    ↓ spawns at random times in 3 time windows
              query.py (Python scraper)
                    ↓ Selenium + ChromeDriver
              CTrip website scraping
                    ↓
              flights_{from}_{to}_{date}.json + flights_history.xlsx
```

**Key Decision**: Go scheduler wraps Python scraper (not pure Python) for:
- Reliable background service on Windows
- No external cron/task scheduler dependency
- Easy `.exe` distribution to non-technical users

## Critical Workflows

### Running Queries Manually
```bash
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25 [--no-headless] [--debug]
```

### Building & Running Scheduler
```bash
# Build Go executable
go build -o AirTicket.exe AirTicket.go

# Start background service (via batch file)
.\start.bat  # Starts AirTicket.exe hidden, logs to logs\scheduler.log

# Stop service
.\stop.bat   # Kills AirTicket.exe process
```

### Python Environment Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install selenium webdriver-manager beautifulsoup4 openpyxl
```

## Project-Specific Conventions

### City Code System
All city references use **3-letter IATA codes** (lowercase in code, uppercase in logs):
- `CITY_LABELS` dict in `query.py` (lines 18-29): maps codes to Chinese names
- Never hardcode city names - always use `city_name()` helper function
- Example: `hgh` → 杭州, `sha` → 上海, `akl` → 奥克兰

### Scraping Anti-Detection Patterns
The scraper uses multiple strategies to avoid bot detection (lines 38-65):
```python
options.add_argument('--disable-images')  # Performance: don't load images
options.add_argument('user-agent=Mozilla/5.0...')  # Mimic real browser
options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

**Multiple CSS Selectors**: Always provide fallback selectors (lines 127-133) since CTrip's HTML structure changes:
```python
selectors = [
    ('div', {'class': 'item-inner'}),
    ('div', {'class': 'product'}),
    # ... more fallbacks
]
```

### Direct Flight Filtering Logic
Three-layer filtering in `parse_flight_item()`:
1. **Flight number count**: Multiple flight numbers = transfer (line 222)
2. **Keyword detection**: Reject text containing '经停', '中转', '联程' (lines 230-232)
3. **Time pair count**: >2 time pairs = transfer (lines 243-245)

Price extraction uses range filtering (1000-50000 CNY) to avoid false positives from small numbers like tax amounts (line 256).

### Excel Output Design
**Each flight gets its own sheet** (not rows in one sheet):
- Sheet naming: `{dep_city}-{arr_city}_{date}_{airline}_{flight_no}` (line 289)
- Appends rows on each query → tracks price changes over time
- 31-char sheet name limit enforced (lines 293-294)

### Logging Convention
All user-facing output uses `log_print()` with ISO 8601 timestamps (lines 31-33):
```python
def log_print(msg):
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"{timestamp} {msg}")
```
Use Unicode symbols: ? (success), ? (error), ? (warning), ? (tip)

## Scheduler Configuration

Edit `config.json` to add/remove query tasks:
```json
{
  "queries": [
    {"from": "sha", "to": "akl", "date": "2026-09-25"}
  ]
}
```

**Time Windows** (in `AirTicket.go` lines 24-28):
```go
var timeWindows = [][2]int{
    {10, 12}, {14, 16}, {18, 20}  // Random time picked within each window daily
}
```
Randomization prevents CTrip from detecting scheduled bot activity.

## External Dependencies

- **ChromeDriver**: Auto-managed by `webdriver-manager` (no manual install needed)
- **Headless Chrome**: Default mode; use `--no-headless` flag for debugging HTML changes
- **Go runtime**: Only needed for building scheduler; end-users run `.exe`

## Debugging Web Scraping Issues

When scraper returns 0 flights:
1. Check `debug_page.html` (auto-saved if `--debug` flag or page <1000 bytes)
2. Verify CSS selectors against saved HTML
3. Run with `--no-headless` to visually inspect what Chrome sees
4. Check if CTrip URL format changed (line 372 in `build_url()`)

Common failure: CTrip detects automation → shows CAPTCHA or empty results.
