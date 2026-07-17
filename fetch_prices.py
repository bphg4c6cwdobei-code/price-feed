"""
gh-feed: publish your watchlist's daily prices as CORS-open JSON via GitHub Actions.
Runs on GitHub's servers (no CORS there), commits docs/prices.json,
which raw.githubusercontent.com serves with Access-Control-Allow-Origin: *.
Powered by yfinance (github.com/ranaroussi/yfinance).
"""
import json, os, datetime
import yfinance as yf

# Edit your watchlist. Keep SPY first — the dashboard uses it as the beta benchmark.
WATCH = ["SPY", "QQQ", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSM", "ASML", "BABA", "GLD", "EEM"]

def series_for(df):
    df = df.dropna(subset=["Close"])
    return {
        "closes":  [round(float(x), 4) for x in df["Close"].tolist()],
        "volumes": [int(x) if x == x else 0 for x in df["Volume"].fillna(0).tolist()],
    }

def main():
    out = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "series": {}}
    data = yf.download(WATCH, period="1y", interval="1d", group_by="ticker",
                       auto_adjust=True, progress=False, threads=True)
    for s in WATCH:
        try:
            df = data[s] if len(WATCH) > 1 else data
            rec = series_for(df)
            if len(rec["closes"]) >= 40:
                out["series"][s] = rec
        except Exception as e:
            print(f"skip {s}: {e}")
    os.makedirs("docs", exist_ok=True)
    with open("docs/prices.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    rows = sum(len(v["closes"]) for v in out["series"].values())
    print(f"wrote docs/prices.json — {len(out['series'])} symbols, {rows} rows")

if __name__ == "__main__":
    main()
