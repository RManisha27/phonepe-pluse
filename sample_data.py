"""Synthetic PhonePe-like data so the dashboard runs without cloning the real repo."""
import numpy as np, pandas as pd

STATES = ["Andaman & Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
          "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
          "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Madhya Pradesh",
          "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry",
          "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
          "Uttarakhand", "West Bengal"]
CATS = ["Recharge & bill payments", "Peer-to-peer payments", "Merchant payments",
        "Financial Services", "Others"]
BRANDS = ["Xiaomi", "Samsung", "Vivo", "Oppo", "Realme", "Apple", "Motorola", "OnePlus"]


def demo_tables(seed=7):
    r = np.random.default_rng(seed)
    w = {s: r.uniform(.3, 3) for s in STATES}
    keys = [(s, y, q) for s in STATES for y in range(2018, 2025) for q in range(1, 5)]
    g = lambda y, q: 1 + ((y - 2018) * 4 + q) * .35
    T = {}
    rows = []
    for s, y, q in keys:
        for c, cw in zip(CATS, [1.2, 2, 1.6, .2, .5]):
            n = int(1e6 * w[s] * cw * g(y, q) * r.uniform(.8, 1.2))
            rows.append((s, y, q, c, n, n * r.uniform(600, 2500) * (3 if c == "Financial Services" else 1)))
    T["aggregated_transaction"] = pd.DataFrame(rows, columns="state year quarter category txn_count amount".split())
    rows = []
    for s, y, q in keys:
        ru = int(2e5 * w[s] * g(y, q))
        sh = r.dirichlet(np.ones(len(BRANDS)))
        for b, p in zip(BRANDS, sh):
            rows.append((s, y, q, ru, ru * int(r.integers(8, 20)), b, int(ru * p), p))
    T["aggregated_user"] = pd.DataFrame(rows, columns="state year quarter registered_users app_opens brand brand_count brand_pct".split())
    rows = [(s, y, q, "Insurance", int(2e3 * w[s] * g(y, q) ** 1.5), 0) for s, y, q in keys]
    ins = pd.DataFrame(rows, columns="state year quarter category txn_count amount".split())
    ins["amount"] = ins.txn_count * r.uniform(900, 3000, len(ins))
    T["aggregated_insurance"] = ins
    mt, mu, mi = [], [], []
    for s, y, q in keys:
        for d in range(1, 5):
            dn, dw = f"{s.split()[0]} District {d}", r.uniform(.1, 1)
            n = int(3e5 * w[s] * dw * g(y, q))
            mt.append((s, y, q, dn, n, n * r.uniform(700, 2200)))
            ru = int(6e4 * w[s] * dw * g(y, q))
            mu.append((s, y, q, dn, ru, ru * int(r.integers(8, 20))))
            m = int(600 * w[s] * dw * g(y, q))
            mi.append((s, y, q, dn, m, m * r.uniform(900, 3000)))
    T["map_map"] = pd.DataFrame(mt, columns="state year quarter district txn_count amount".split())
    T["map_user"] = pd.DataFrame(mu, columns="state year quarter district registered_users app_opens".split())
    T["map_insurance"] = pd.DataFrame(mi, columns="state year quarter district txn_count amount".split())
    # top tables (country level)
    def top(src, valcols):
        out = []
        for (y, q), g_ in src.groupby(["year", "quarter"]):
            st = g_.groupby("state")[valcols].sum().nlargest(10, valcols[0]).reset_index()
            dt = g_.nlargest(10, valcols[0])
            for lv, df, col in (("state", st, "state"), ("district", dt, "district")):
                for _, x in df.iterrows():
                    out.append((("India"), y, q, lv, x[col], *[x[c] for c in valcols]))
            for i in range(10):
                out.append(("India", y, q, "pincode", str(int(r.integers(100000, 999999))),
                            *[x[c] * r.uniform(.05, .3) for c in valcols]))
        return pd.DataFrame(out, columns=["state", "year", "quarter", "level", "entity", *valcols])
    T["top_map"] = top(T["map_map"], ["txn_count", "amount"])
    T["top_insurance"] = top(T["map_insurance"], ["txn_count", "amount"])
    T["top_user"] = top(T["map_user"], ["registered_users"])
    return T
