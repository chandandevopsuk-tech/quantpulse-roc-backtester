# QuantPulse — Event-Driven ROC Backtester

A transparent **rate-of-change (ROC) zero-crossing** strategy engine for testing daily OHLC candle data. A crossing is confirmed at candle close and executed at the **next candle open**, explicitly avoiding same-candle lookahead.

## Includes
- ROC parameter (default 12), BUY/SELL crossover detection, long/short reversals
- Configurable units, entry and exit fees, slippage, mark-to-market equity and max drawdown
- Typed REST API and CSV CLI, repeatable deterministic test suite

## Quick start
```bash
python -m pip install -e '.[dev]'
pytest
uvicorn quantpulse.api:app --reload
# POST /v1/backtest in /docs, or:
python -m quantpulse.cli examples/ohlc.csv --period 3 --output report.json
```

**Security / trading risk:** Research and educational software; this is **not** an investment recommendation or live execution system. Market data quality, trading calendars, borrow costs, spreads, contract size, margin, corporate actions and taxes are outside this simulation. Validate with out-of-sample data before drawing any conclusions.
