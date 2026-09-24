import streamlit as st
import pandas as pd
import json
import requests
import zipfile
import shutil
from pathlib import Path
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PhonePe Pulse - Interactive Dashboard",
    page_icon="📱",
    layout="wide"
)


# ============================================================
# DOWNLOAD PHONEPE DATA
# ============================================================

DATA_DIR = Path("/tmp/phonepe_data")
ZIP_PATH = Path("/tmp/phonepe.zip")

PHONEPE_URL = (
    "https://github.com/PhonePe/pulse/"
    "archive/refs/heads/main.zip"
)


@st.cache_resource
def download_phonepe_data():

    if DATA_DIR.exists():
        return DATA_DIR

    try:

        with st.spinner(
            "Downloading PhonePe Pulse data..."
        ):

            response = requests.get(
                PHONEPE_URL,
                timeout=180
            )

            response.raise_for_status()

            with open(
                ZIP_PATH,
                "wb"
            ) as f:
                f.write(response.content)

        with st.spinner(
            "Extracting PhonePe data..."
        ):

            with zipfile.ZipFile(
                ZIP_PATH,
                "r"
            ) as zip_ref:

                zip_ref.extractall(
                    "/tmp"
                )

        extracted_folder = Path(
            "/tmp/pulse-main"
        )

        if not extracted_folder.exists():

            st.error(
                "PhonePe repository could not be extracted."
            )

            st.stop()

        shutil.move(
            str(extracted_folder / "data"),
            str(DATA_DIR)
        )

        return DATA_DIR

    except Exception as e:

        st.error(
            f"Unable to download PhonePe data: {e}"
        )

        st.stop()


DATA = download_phonepe_data()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_state(state):

    return (
        str(state)
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def get_quarter(file_name):

    return int(
        Path(file_name).stem
    )


# ============================================================
# LOAD AGGREGATED TRANSACTIONS
# ============================================================

@st.cache_data
def load_transactions():

    path = (
        DATA
        / "aggregated"
        / "transaction"
        / "country"
        / "india"
        / "state"
    )

    records = []

    for state_folder in path.iterdir():

        if not state_folder.is_dir():
            continue

        for year_folder in state_folder.iterdir():

            if not year_folder.is_dir():
                continue

            for file in year_folder.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = json.load(f)

                    transaction_data = (
                        content
                        .get("data", {})
                        .get("transactionData", [])
                    )

                    for item in transaction_data:

                        instruments = item.get(
                            "paymentInstruments",
                            []
                        )

                        if not instruments:
                            continue

                        metric = instruments[0]

                        records.append({

                            "State":
                                format_state(
                                    state_folder.name
                                ),

                            "Year":
                                int(
                                    year_folder.name
                                ),

                            "Quarter":
                                get_quarter(
                                    file.name
                                ),

                            "Transaction Type":
                                item.get(
                                    "name",
                                    "Unknown"
                                ),

                            "Transaction Count":
                                metric.get(
                                    "count",
                                    0
                                ),

                            "Transaction Amount":
                                metric.get(
                                    "amount",
                                    0
                                )
                        })

                except Exception:
                    continue

    return pd.DataFrame(records)


# ============================================================
# LOAD MAP TRANSACTIONS
# ============================================================

@st.cache_data
def load_map_transactions():

    path = (
        DATA
        / "map"
        / "transaction"
        / "hover"
        / "country"
        / "india"
        / "state"
    )

    records = []

    if not path.exists():
        return pd.DataFrame()

    for state_folder in path.iterdir():

        if not state_folder.is_dir():
            continue

        for year_folder in state_folder.iterdir():

            if not year_folder.is_dir():
                continue

            for file in year_folder.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = json.load(f)

                    district_data = (
                        content
                        .get("data", {})
                        .get("hoverDataList", [])
                    )

                    for item in district_data:

                        metrics = item.get(
                            "metric",
                            []
                        )

                        if not metrics:
                            continue

                        metric = metrics[0]

                        records.append({

                            "State":
                                format_state(
                                    state_folder.name
                                ),

                            "District":
                                str(
                                    item.get(
                                        "name",
                                        ""
                                    )
                                ).replace(
                                    "district",
                                    ""
                                ).strip().title(),

                            "Year":
                                int(
                                    year_folder.name
                                ),

                            "Quarter":
                                get_quarter(
                                    file.name
                                ),

                            "Transaction Count":
                                metric.get(
                                    "count",
                                    0
                                ),

                            "Transaction Amount":
                                metric.get(
                                    "amount",
                                    0
                                )
                        })

                except Exception:
                    continue

    return pd.DataFrame(records)


# ============================================================
# LOAD TOP TRANSACTIONS
# ============================================================

@st.cache_data
def load_top_transactions():

    path = (
        DATA
        / "top"
        / "transaction"
        / "country"
        / "india"
        / "state"
    )

    records = []

    if not path.exists():
        return pd.DataFrame()

    for state_folder in path.iterdir():

        if not state_folder.is_dir():
            continue

        for year_folder in state_folder.iterdir():

            if not year_folder.is_dir():
                continue

            for file in year_folder.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = json.load(f)

                    pincodes = (
                        content
                        .get("data", {})
                        .get("pincodes", [])
                    )

                    for item in pincodes:

                        metric = item.get(
                            "metric",
                            {}
                        )

                        records.append({

                            "State":
                                format_state(
                                    state_folder.name
                                ),

                            "Pincode":
                                item.get(
                                    "entityName",
                                    ""
                                ),

                            "Year":
                                int(
                                    year_folder.name
                                ),

                            "Quarter":
                                get_quarter(
                                    file.name
                                ),

                            "Transaction Count":
                                metric.get(
                                    "count",
                                    0
                                ),

                            "Transaction Amount":
                                metric.get(
                                    "amount",
                                    0
                                )
                        })

                except Exception:
                    continue

    return pd.DataFrame(records)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    "Preparing dashboard..."
):

    transactions = load_transactions()

    map_data = load_map_transactions()

    top_data = load_top_transactions()


if transactions.empty:

    st.error(
        "Transaction data could not be loaded."
    )

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title(
    "📱 PhonePe Pulse"
)

st.subheader(
    "Interactive India Transaction Insights Dashboard"
)

st.write(
    "Explore PhonePe transaction patterns across "
    "Indian states and districts using interactive "
    "maps, filters and visualizations."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "🔎 Filters"
)


years = sorted(
    transactions["Year"].unique()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years) - 1
)


quarters = sorted(
    transactions[
        transactions["Year"] == selected_year
    ]["Quarter"].unique()
)

selected_quarter = st.sidebar.selectbox(
    "Select Quarter",
    quarters
)


transaction_types = sorted(
    transactions[
        (
            transactions["Year"]
            == selected_year
        )
        &
        (
            transactions["Quarter"]
            == selected_quarter
        )
    ]["Transaction Type"].unique()
)


selected_type = st.sidebar.selectbox(
    "Transaction Type",
    ["All"] + transaction_types
)


map_metric = st.sidebar.radio(
    "Map Metric",
    [
        "Transaction Amount",
        "Transaction Count"
    ]
)


# ============================================================
# FILTER TRANSACTIONS
# ============================================================

filtered = transactions[
    (
        transactions["Year"]
        == selected_year
    )
    &
    (
        transactions["Quarter"]
        == selected_quarter
    )
].copy()


if selected_type != "All":

    filtered = filtered[
        filtered["Transaction Type"]
        == selected_type
    ]


# ============================================================
# STATE SUMMARY
# ============================================================

state_summary = (
    filtered
    .groupby("State")
    [
        [
            "Transaction Count",
            "Transaction Amount"
        ]
    ]
    .sum()
    .reset_index()
)


# ============================================================
# KPI
# ============================================================

total_transactions = state_summary[
    "Transaction Count"
].sum()

total_amount = state_summary[
    "Transaction Amount"
].sum()

state_count = state_summary[
    "State"
].nunique()


c1, c2, c3 = st.columns(3)


with c1:

    st.metric(
        "Total Transactions",
        f"{total_transactions:,.0f}"
    )


with c2:

    st.metric(
        "Transaction Amount",
        f"₹{total_amount:,.2f}"
    )


with c3:

    st.metric(
        "States",
        state_count
    )


# ============================================================
# INDIA INTERACTIVE MAP
# ============================================================

st.header(
    "🗺️ Interactive India State Map"
)

st.write(
    f"Showing {map_metric} for "
    f"{selected_year} - Q{selected_quarter}"
)


# State map using Plotly's built-in India locations

try:

    fig_map = px.choropleth(
        state_summary,
        locations="State",
        locationmode="geojson-id",
        color=map_metric,
        hover_name="State",
        hover_data={
            "Transaction Count": ":,.0f",
            "Transaction Amount": ":,.2f"
        },
        title=(
            f"PhonePe {map_metric} "
            f"- {selected_year} Q{selected_quarter}"
        )
    )

    fig_map.update_geos(
        scope="asia",
        center={
            "lat": 22.5,
            "lon": 79.0
        },
        projection_scale=4
    )

    fig_map.update_layout(
        height=650,
        margin=dict(
            l=0,
            r=0,
            t=60,
            b=0
        )
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

except Exception:

    st.info(
        "The state data is available below "
        "even if the map boundary is unavailable."
    )


# ============================================================
# STATE BAR CHART
# ============================================================

st.header(
    "🏆 State-wise Transaction Analysis"
)


top_states = (
    state_summary
    .sort_values(
        map_metric,
        ascending=False
    )
    .head(10)
)


fig_states = px.bar(
    top_states,
    x=map_metric,
    y="State",
    orientation="h",
    title=f"Top 10 States by {map_metric}",
    text_auto=".2s"
)

fig_states.update_layout(
    yaxis={
        "categoryorder":
        "total ascending"
    }
)

st.plotly_chart(
    fig_states,
    use_container_width=True
)


# ============================================================
# TRANSACTION TYPE
# ============================================================

st.header(
    "💳 Transaction Category Analysis"
)


category_data = (
    filtered
    .groupby(
        "Transaction Type"
    )
    [
        [
            "Transaction Count",
            "Transaction Amount"
        ]
    ]
    .sum()
    .reset_index()
)


col1, col2 = st.columns(2)


with col1:

    fig = px.pie(
        category_data,
        names="Transaction Type",
        values="Transaction Amount",
        title="Transaction Amount by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    fig = px.bar(
        category_data,
        x="Transaction Type",
        y="Transaction Count",
        title="Transaction Count by Category",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# DISTRICT ANALYSIS
# ============================================================

st.header(
    "📍 District-level Analysis"
)


if not map_data.empty:

    district_filtered = map_data[
        (
            map_data["Year"]
            == selected_year
        )
        &
        (
            map_data["Quarter"]
            == selected_quarter
        )
    ].copy()


    selected_state = st.selectbox(
        "Select State for District Analysis",
        sorted(
            district_filtered[
                "State"
            ].unique()
        )
    )


    district_filtered = district_filtered[
        district_filtered["State"]
        == selected_state
    ]


    district_summary = (
        district_filtered
        .groupby("District")
        [
            [
                "Transaction Count",
                "Transaction Amount"
            ]
        ]
        .sum()
        .reset_index()
        .sort_values(
            "Transaction Amount",
            ascending=False
        )
    )


    fig_district = px.bar(
        district_summary.head(15),
        x="Transaction Amount",
        y="District",
        orientation="h",
        title=(
            f"Top Districts in "
            f"{selected_state}"
        ),
        text_auto=".2s"
    )

    fig_district.update_layout(
        yaxis={
            "categoryorder":
            "total ascending"
        }
    )

    st.plotly_chart(
        fig_district,
        use_container_width=True
    )


    st.dataframe(
        district_summary,
        use_container_width=True
    )

else:

    st.warning(
        "District data is not available "
        "for this data release."
    )


# ============================================================
# PINCODE ANALYSIS
# ============================================================

st.header(
    "📌 Top Pincode Analysis"
)


if not top_data.empty:

    pincode_data = top_data[
        (
            top_data["Year"]
            == selected_year
        )
        &
        (
            top_data["Quarter"]
            == selected_quarter
        )
    ]


    pincode_summary = (
        pincode_data
        .groupby("Pincode")
        [
            [
                "Transaction Count",
                "Transaction Amount"
            ]
        ]
        .sum()
        .reset_index()
        .sort_values(
            "Transaction Amount",
            ascending=False
        )
        .head(10)
    )


    fig_pin = px.bar(
        pincode_summary,
        x="Transaction Amount",
        y="Pincode",
        orientation="h",
        title="Top 10 Pincodes by Transaction Amount",
        text_auto=".2s"
    )

    fig_pin.update_layout(
        yaxis={
            "categoryorder":
            "total ascending"
        }
    )

    st.plotly_chart(
        fig_pin,
        use_container_width=True
    )


# ============================================================
# TREND ANALYSIS
# ============================================================

st.header(
    "📈 Transaction Trend"
)


trend = (
    transactions
    .groupby(
        [
            "Year",
            "Quarter"
        ]
    )
    [
        [
            "Transaction Count",
            "Transaction Amount"
        ]
    ]
    .sum()
    .reset_index()
)


trend["Period"] = (
    trend["Year"].astype(str)
    + " Q"
    + trend["Quarter"].astype(str)
)


fig_trend = px.line(
    trend,
    x="Period",
    y="Transaction Amount",
    markers=True,
    title="Transaction Amount Trend"
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)


# ============================================================
# DATA TABLE
# ============================================================

st.header(
    "📋 State Data"
)

st.dataframe(
    state_summary.sort_values(
        map_metric,
        ascending=False
    ),
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "PhonePe Transaction Insights | "
    "Python | Pandas | Plotly | Streamlit"
)
