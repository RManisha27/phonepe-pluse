"""PhonePe Transaction Insights - Streamlit dashboard.  Run:  streamlit run app.py"""
import json, os, re
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from sqlalchemy import create_engine, inspect, text

st.set_page_config(page_title="PhonePe Transaction Insights", page_icon="💜", layout="wide")
GEO_URL = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/"
           "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states_geo.json")


# ---------------------------------------------------------------- data layer
@st.cache_resource
def engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            url = st.secrets["DATABASE_URL"]
        except Exception:
            url = "sqlite:///phonepe.db"
    eng = create_engine(url)
    if "aggregated_transaction" not in inspect(eng).get_table_names():   # first run -> demo data
        from sample_data import demo_tables
        for n, df in demo_tables().items():
            df.to_sql(n, eng, index=False, if_exists="replace", chunksize=5000)
        st.session_state["demo"] = True
    return eng


@st.cache_data(show_spinner=False)
def q(sql, **params):
    return pd.read_sql(text(sql), engine(), params=params)


GEO_URLS = [
    GEO_URL,
    "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States",
    "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
]
ALIAS = {"andamanandnicobarislands": "andaman", "andamanandnicobarisland": "andaman",
         "andamanandnicobar": "andaman", "nctofdelhi": "delhi", "orissa": "odisha",
         "uttaranchal": "uttarakhand", "pondicherry": "puducherry",
         "dadraandnagarhavelianddamananddiu": "dnhdd", "dadaraandnagarhavelli": "dnhdd",
         "dadraandnagarhaveli": "dnhdd", "damananddiu": "dnhdd"}


def norm(s):
    s = re.sub(r"[^a-z0-9]", "", str(s).lower().replace("&", "and"))
    return ALIAS.get(s, s)


@st.cache_data(show_spinner=False)
def india_geojson():
    """Local file india_states.geojson wins; otherwise try several public URLs."""
    gj, errs = None, []
    if os.path.exists("india_states.geojson"):
        gj = json.load(open("india_states.geojson", encoding="utf-8"))
    else:
        for url in GEO_URLS:
            try:
                r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                gj = r.json()
                break
            except Exception as e:
                errs.append(f"{url} -> {e}")
    if gj is not None:
        for f in gj["features"]:
            pr = f["properties"]
            name = next((pr[k] for k in ("ST_NM", "NAME_1", "st_nm", "name", "NAME") if k in pr), "")
            pr["key"] = norm(name)
    return gj, errs


def fmt(n):
    n = float(n or 0)
    for div, s in ((1e7, " Cr"), (1e5, " L"), (1e3, " K")):
        if n >= div:
            return f"{n / div:,.2f}{s}"
    return f"{n:,.0f}"


# ---------------------------------------------------------------- sidebar
engine()
st.sidebar.title("💜 PhonePe Pulse")
page = st.sidebar.radio("Navigate", ["Overview", "Transactions", "Users", "Insurance",
                                     "Geo Map", "Top Performers", "Business Case Studies"])
years = q("SELECT DISTINCT year FROM aggregated_transaction ORDER BY year")["year"].tolist()
year = st.sidebar.selectbox("Year", ["All"] + years, index=len(years))
quarter = st.sidebar.selectbox("Quarter", ["All", 1, 2, 3, 4])
W, P = " WHERE 1=1", {}
if year != "All":
    W += " AND year=:y"; P["y"] = int(year)
if quarter != "All":
    W += " AND quarter=:q"; P["q"] = int(quarter)
if st.session_state.get("demo"):
    st.sidebar.warning("Showing synthetic demo data. Run `python etl.py --data pulse/data` to load real data.")

st.title("PhonePe Transaction Insights")

# ---------------------------------------------------------------- pages
if page == "Overview":
    t = q(f"SELECT SUM(txn_count) c, SUM(amount) a FROM aggregated_transaction{W}", **P).iloc[0]
    u = q(f"SELECT SUM(registered_users) r, SUM(app_opens) o FROM map_user{W}", **P).iloc[0]
    i = q(f"SELECT SUM(txn_count) c, SUM(amount) a FROM aggregated_insurance{W}", **P).iloc[0]
    c = st.columns(5)
    c[0].metric("Transactions", fmt(t.c)); c[1].metric("Payment value (₹)", fmt(t.a))
    c[2].metric("Avg ticket (₹)", f"{t.a / t.c:,.0f}" if t.c else "-")
    c[3].metric("Registered users", fmt(u.r)); c[4].metric("Insurance policies", fmt(i.c))
    tr = q("SELECT year, quarter, SUM(amount) amount, SUM(txn_count) txns FROM aggregated_transaction "
           "GROUP BY year, quarter ORDER BY year, quarter")
    tr["period"] = tr.year.astype(str) + " Q" + tr.quarter.astype(str)
    st.plotly_chart(px.line(tr, x="period", y="amount", markers=True, title="Payment value by quarter"),
                    use_container_width=True)

elif page == "Transactions":
    cat = q(f"SELECT category, SUM(txn_count) txns, SUM(amount) amount FROM aggregated_transaction{W} "
            "GROUP BY category ORDER BY amount DESC", **P)
    a, b = st.columns(2)
    a.plotly_chart(px.pie(cat, names="category", values="amount", hole=.4,
                          title="Share of payment value by category"), use_container_width=True)
    b.plotly_chart(px.bar(cat, x="category", y="txns", title="Transaction count by category"),
                   use_container_width=True)
    stt = q(f"SELECT state, SUM(amount) amount FROM aggregated_transaction{W} GROUP BY state "
            "ORDER BY amount DESC LIMIT 15", **P)
    st.plotly_chart(px.bar(stt, x="amount", y="state", orientation="h", title="Top 15 states by value")
                    .update_yaxes(autorange="reversed"), use_container_width=True)

elif page == "Users":
    dev = q(f"SELECT brand, SUM(brand_count) users FROM aggregated_user{W} AND brand IS NOT NULL "
            "GROUP BY brand ORDER BY users DESC", **P)
    a, b = st.columns(2)
    if not dev.empty:
        a.plotly_chart(px.pie(dev, names="brand", values="users", title="Device brand share"),
                       use_container_width=True)
    eng = q(f"SELECT state, SUM(registered_users) users, SUM(app_opens)*1.0/SUM(registered_users) opens_per_user "
            f"FROM map_user{W} GROUP BY state ORDER BY users DESC LIMIT 15", **P)
    b.plotly_chart(px.bar(eng, x="state", y="opens_per_user", title="App opens per registered user (top 15 states)"),
                   use_container_width=True)
    st.plotly_chart(px.bar(eng, x="state", y="users", title="Registered users - top 15 states"),
                    use_container_width=True)

elif page == "Insurance":
    trend = q("SELECT year, SUM(txn_count) policies, SUM(amount) amount FROM aggregated_insurance "
              "GROUP BY year ORDER BY year")
    a, b = st.columns(2)
    a.plotly_chart(px.bar(trend, x="year", y="policies", title="Policies purchased per year"),
                   use_container_width=True)
    stt = q(f"SELECT state, SUM(txn_count) policies, SUM(amount) amount FROM aggregated_insurance{W} "
            "GROUP BY state ORDER BY amount DESC LIMIT 10", **P)
    b.plotly_chart(px.bar(stt, x="state", y="amount", title="Top 10 states by insurance value"),
                   use_container_width=True)
    dist = q(f"SELECT state, district, SUM(txn_count) policies, SUM(amount) amount FROM map_insurance{W} "
             "GROUP BY state, district ORDER BY amount DESC LIMIT 10", **P)
    st.subheader("Top 10 districts"); st.dataframe(dist, use_container_width=True, hide_index=True)

elif page == "Geo Map":
    src = st.radio("Dataset", ["Transactions", "Insurance", "Users"], horizontal=True)
    if src == "Users":
        df = q(f"SELECT state, SUM(registered_users) value FROM map_user{W} GROUP BY state", **P)
    else:
        tbl = "aggregated_transaction" if src == "Transactions" else "aggregated_insurance"
        df = q(f"SELECT state, SUM(amount) value FROM {tbl}{W} GROUP BY state", **P)
    df["key"] = df.state.map(norm)
    gj, geo_errs = india_geojson()
    if gj:
        fig = px.choropleth(df, geojson=gj, locations="key", featureidkey="properties.key", color="value",
                            hover_name="state", color_continuous_scale="Purples")
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=650, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not load the India map file - showing a bar chart instead.")
        with st.expander("Why? (technical details)"):
            st.write(geo_errs)
            st.write("Fix: download any India states GeoJSON and save it next to app.py as india_states.geojson")
        st.plotly_chart(px.bar(df.sort_values("value"), x="value", y="state", orientation="h", height=800),
                        use_container_width=True)
    st.subheader("District level")
    s = st.selectbox("State", sorted(df.state))
    d = q(f"SELECT district, SUM(txn_count) txns, SUM(amount) amount FROM map_map{W} AND state=:s "
          "GROUP BY district ORDER BY amount DESC", s=s, **P)
    st.plotly_chart(px.bar(d, x="district", y="amount"), use_container_width=True)

elif page == "Top Performers":
    ds = st.radio("Dataset", ["Transactions", "Insurance", "Users"], horizontal=True, key="topds")
    tbl = {"Transactions": "top_map", "Insurance": "top_insurance", "Users": "top_user"}[ds]
    val = "registered_users" if ds == "Users" else "amount"
    cols = st.columns(3)
    for col, lv in zip(cols, ["state", "district", "pincode"]):
        d = q(f"SELECT entity, SUM({val}) value FROM {tbl}{W} AND level=:l GROUP BY entity "
              "ORDER BY value DESC LIMIT 10", l=lv, **P)
        col.subheader(f"Top {lv}s")
        col.plotly_chart(px.bar(d, x="value", y="entity", orientation="h").update_yaxes(autorange="reversed"),
                         use_container_width=True)

else:  # Business Case Studies
    CASES = {
        "1. Payment category popularity": "SELECT category, SUM(txn_count) txns, SUM(amount) amount FROM aggregated_transaction GROUP BY category ORDER BY amount DESC",
        "2. Top 10 states by payment value": "SELECT state, SUM(amount) amount FROM aggregated_transaction GROUP BY state ORDER BY amount DESC LIMIT 10",
        "3. Year-over-year growth": "SELECT year, SUM(amount) amount, SUM(txn_count) txns FROM aggregated_transaction GROUP BY year ORDER BY year",
        "4. Quarterly seasonality": "SELECT quarter, SUM(amount) amount FROM aggregated_transaction GROUP BY quarter ORDER BY quarter",
        "5. Avg ticket size by category (segmentation)": "SELECT category, SUM(amount)*1.0/SUM(txn_count) avg_ticket FROM aggregated_transaction GROUP BY category ORDER BY avg_ticket DESC",
        "6. Top 10 districts by transactions": "SELECT state, district, SUM(txn_count) txns FROM map_map GROUP BY state, district ORDER BY txns DESC LIMIT 10",
        "7. Device brand share": "SELECT brand, SUM(brand_count) users FROM aggregated_user WHERE brand IS NOT NULL GROUP BY brand ORDER BY users DESC",
        "8. App engagement (opens per user) - top 10 states": "SELECT state, SUM(app_opens)*1.0/SUM(registered_users) opens_per_user FROM map_user GROUP BY state ORDER BY opens_per_user DESC LIMIT 10",
        "9. Top 10 states for insurance": "SELECT state, SUM(txn_count) policies, SUM(amount) amount FROM aggregated_insurance GROUP BY state ORDER BY amount DESC LIMIT 10",
        "10. Outlier screening: highest avg ticket by state (fraud proxy)": "SELECT state, SUM(amount)*1.0/SUM(txn_count) avg_ticket FROM aggregated_transaction GROUP BY state ORDER BY avg_ticket DESC LIMIT 10",
    }
    name = st.selectbox("Case study", list(CASES))
    sql = CASES[name]
    st.code(sql, language="sql")
    df = q(sql)
    a, b = st.columns([1, 1.4])
    a.dataframe(df, use_container_width=True, hide_index=True)
    num = df.select_dtypes("number").columns[-1]
    lab = df.select_dtypes(exclude="number").columns
    x = lab[-1] if len(lab) else df.columns[0]
    b.plotly_chart(px.bar(df, x=x, y=num), use_container_width=True)
    st.info("Write your own insight + recommendation for each case here in the report/PPT deliverable.")
