# PhonePe Transaction Insights (Streamlit)

Pipeline: **PhonePe Pulse JSON → SQL (9 tables) → SQL analysis → Plotly charts → Streamlit dashboard**

## Run locally
```bash
pip install -r requirements.txt
git clone https://github.com/PhonePe/pulse.git
python etl.py --data pulse/data          # builds phonepe.db (SQLite)
streamlit run app.py
```
No data yet? `streamlit run app.py` auto-creates a synthetic demo DB (or `python etl.py --demo`).

MySQL / PostgreSQL: `python etl.py --data pulse/data --db mysql+pymysql://user:pwd@host/phonepe`
then set the same URL as env var `DATABASE_URL` (or in Streamlit secrets) for the app.

## Tables
aggregated_user / aggregated_transaction / aggregated_insurance,
map_user / map_map / map_insurance, top_user / top_map / top_insurance.

## Dashboard pages
Overview · Transactions · Users · Insurance · Geo Map (state choropleth + district drill-down) ·
Top Performers (states / districts / pincodes) · Business Case Studies (10 SQL queries with charts).

## Deploy online (Streamlit Community Cloud - free)
1. Push this folder to a GitHub repo (include `phonepe.db` if it is < 100 MB, or use a hosted MySQL/Postgres).
2. Go to share.streamlit.io → **New app** → pick repo, branch, file `app.py`.
3. If using a hosted DB: Settings → Secrets → `DATABASE_URL = "mysql+pymysql://..."`.
4. Deploy - you get a public URL like `https://<your-app>.streamlit.app`.

Note: Pulse state names differ slightly from the GeoJSON names; aliases live in `norm()` in `app.py`.
