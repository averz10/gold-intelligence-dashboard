# Gold Intelligence MVP V10 - Supabase Persistent Logging

V10 replaces the blocked Google Sheets approach with Supabase persistent logging.

## What V10 adds

1. Supabase persistent logging
   - Local CSV logging still works immediately.
   - Optional Supabase logging can be enabled through Streamlit secrets.
   - Supabase history can be loaded back into the dashboard.
   - Supabase history can be downloaded as CSV.

2. Keeps V9 improvements
   - Spot XAUUSD
   - Gold Futures as reference
   - Automatic macro data
   - Fed Tone Intelligence
   - Filtered gold news
   - Driver Explanation Panel
   - Score Logger
   - Trade Permission Rules

## Run locally on Windows

```cmd
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m streamlit run app.py
```

Or double-click:

```text
RUN_DASHBOARD_WINDOWS.bat
```

## Daily use

1. Press **Fetch market data now**.
2. Press **Fetch Fed tone now**.
3. Press **Fetch gold news now**.
4. Manually set geopolitical risk.
5. Add a snapshot note if useful.
6. Press **Save current bias snapshot**.
7. Download the local CSV regularly.
8. If Supabase is configured, turn on **Also save to Supabase**.

## Important

This is still a bias/permission dashboard, not a trade signal.

TradingView structure still decides entries.
