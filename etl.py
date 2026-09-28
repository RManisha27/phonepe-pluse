"""ETL: PhonePe Pulse JSON  ->  SQL tables.

  git clone https://github.com/PhonePe/pulse.git
  python etl.py --data pulse/data                    # SQLite (phonepe.db)
  python etl.py --data pulse/data --db mysql+pymysql://user:pwd@host/phonepe
  python etl.py --demo                               # synthetic data, no clone needed
"""
import argparse, json, os
import pandas as pd
from sqlalchemy import create_engine


def _files(base):
    for d, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".json"):
                yield os.path.join(d, f)


def _meta(path, base):
    p = os.path.relpath(path, base).replace("\\", "/").split("/")
    state = p[1].replace("-", " ").title() if p[0] == "state" else None
    return state, int(p[-2]), int(p[-1].split(".")[0])


def _load(base, fn):
    rows = []
    for path in _files(base):
        st, y, q = _meta(path, base)
        d = (json.load(open(path, encoding="utf-8")) or {}).get("data") or {}
        rows += fn(d, st, y, q)
    return pd.DataFrame(rows)


def _agg_txn(d, s, y, q):   # aggregated transaction + insurance
    return [dict(state=s, year=y, quarter=q, category=t["name"],
                 txn_count=i["count"], amount=i["amount"])
            for t in d.get("transactionData") or [] for i in t["paymentInstruments"]]


def _agg_user(d, s, y, q):
    a = d.get("aggregated") or {}
    dev = d.get("usersByDevice") or [{}]
    return [dict(state=s, year=y, quarter=q, registered_users=a.get("registeredUsers"),
                 app_opens=a.get("appOpens"), brand=b.get("brand"),
                 brand_count=b.get("count"), brand_pct=b.get("percentage")) for b in dev]


def _map_txn(d, s, y, q):   # map transaction + insurance
    return [dict(state=s, year=y, quarter=q, district=h["name"].replace(" district", "").title(),
                 txn_count=m["count"], amount=m["amount"])
            for h in d.get("hoverDataList") or [] for m in h["metric"]]


def _map_user(d, s, y, q):
    return [dict(state=s, year=y, quarter=q, district=k.replace(" district", "").title(),
                 registered_users=v["registeredUsers"], app_opens=v["appOpens"])
            for k, v in (d.get("hoverData") or {}).items()]


def _top(d, s, y, q):       # top transaction + insurance
    return [dict(state=s or "India", year=y, quarter=q, level=lv[:-1], entity=e["entityName"],
                 txn_count=e["metric"]["count"], amount=e["metric"]["amount"])
            for lv in ("states", "districts", "pincodes") for e in d.get(lv) or []]


def _top_user(d, s, y, q):
    return [dict(state=s or "India", year=y, quarter=q, level=lv[:-1], entity=e["name"],
                 registered_users=e["registeredUsers"])
            for lv in ("states", "districts", "pincodes") for e in d.get(lv) or []]


def build_tables(data):
    P = lambda *x: os.path.join(data, *x, "country", "india")
    PH = lambda k: os.path.join(data, "map", k, "hover", "country", "india")
    return {
        "aggregated_user": _load(P("aggregated", "user"), _agg_user),
        "aggregated_transaction": _load(P("aggregated", "transaction"), _agg_txn),
        "aggregated_insurance": _load(P("aggregated", "insurance"), _agg_txn),
        "map_user": _load(PH("user"), _map_user),
        "map_map": _load(PH("transaction"), _map_txn),
        "map_insurance": _load(PH("insurance"), _map_txn),
        "top_user": _load(P("top", "user"), _top_user),
        "top_map": _load(P("top", "transaction"), _top),
        "top_insurance": _load(P("top", "insurance"), _top),
    }


def write(tables, db_url):
    eng = create_engine(db_url)
    for name, df in tables.items():
        df.to_sql(name, eng, if_exists="replace", index=False, chunksize=5000)
        print(f"{name:26s} {len(df):>8,d} rows")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="path to pulse/data")
    ap.add_argument("--db", default="sqlite:///phonepe.db")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        from sample_data import demo_tables
        write(demo_tables(), a.db)
    elif a.data:
        write(build_tables(a.data), a.db)
    else:
        ap.error("give --data <path> or --demo")
