import os
import json
import zipfile
import requests
import shutil
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PhonePe Pulse Dashboard",
    page_icon="📱",
    layout="wide"
)


# ============================================================
# SETTINGS
# ============================================================

REPO_ZIP_URL = (
    "https://github.com/PhonePe/pulse/archive/refs/heads/main.zip"
)

BASE_DIR = Path("/tmp/phonepe_pulse")
DATA_DIR = BASE_DIR / "pulse-main" / "data"


# ============================================================
# DOWNLOAD PHONEPE DATA
# ============================================================

@st.cache_resource
def download_phonepe_data():

    if DATA_DIR.exists():
        return DATA_DIR

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    zip_file = BASE_DIR / "phonepe.zip"

    try:
        with st.spinner("Downloading PhonePe Pulse data..."):

            response = requests.get(
                REPO_ZIP_URL,
                stream=True,
                timeout=180
            )

            response.raise_for_status()

            with open(zip_file, "wb") as f:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if chunk:
                        f.write(chunk)

        with st.spinner("Extracting PhonePe Pulse data..."):

            with zipfile.ZipFile(
                zip_file,
                "r"
            ) as zip_ref:

                zip_ref.extractall(BASE_DIR)

        if not DATA_DIR.exists():

            raise FileNotFoundError(
                "PhonePe data folder was not found after extraction."
            )

        return DATA_DIR

    except Exception as e:

        st.error(
            f"Unable to download PhonePe Pulse data: {e}"
        )

        st.stop()


DATA_ROOT = download_phonepe_data()


# ============================================================
# HELPER
# ============================================================

def clean_name(value):

    if value is None:
        return ""

    return str(value).replace(
        "-", " "
    ).replace(
        "_", " "
    ).title()


def quarter_number(filename):

    return int(
        Path(filename).stem
    )


# ============================================================
# AGGREGATED TRANSACTIONS
# ============================================================

@st.cache_data
def load_aggregated_transactions(data_root):

    path = (
        data_root
        / "aggregated"
        / "transaction"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    transaction_data = (
                        data.get("data", {})
                        .get("transactionData", [])
                    )

                    for item in transaction_data:

                        instruments = item.get(
                            "paymentInstruments",
                            []
                        )

                        if not instruments:
                            continue

                        instrument = instruments[0]

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter": quarter_number(
                                file.name
                            ),
                            "Transaction Type":
                                item.get("name", "Unknown"),
                            "Transaction Count":
                                instrument.get("count", 0),
                            "Transaction Amount":
                                instrument.get("amount", 0)
                        })

                except Exception:
                    continue

    return pd.DataFrame(rows)


# ============================================================
# AGGREGATED USERS
# ============================================================

@st.cache_data
def load_aggregated_users(data_root):

    path = (
        data_root
        / "aggregated"
        / "user"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    info = data.get(
                        "data",
                        {}
                    )

                    # Older PhonePe Pulse format
                    users_by_device = info.get(
                        "usersByDevice",
                        []
                    )

                    for item in users_by_device:

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter": quarter_number(
                                file.name
                            ),
                            "Brand": item.get(
                                "brand",
                                "Unknown"
                            ),
                            "User Count": item.get(
                                "count",
                                0
                            ),
                            "Percentage": item.get(
                                "percentage",
                                0
                            )
                        })

                except Exception:
                    continue

    return pd.DataFrame(rows)


# ============================================================
# MAP TRANSACTIONS
# ============================================================

@st.cache_data
def load_map_transactions(data_root):

    path = (
        data_root
        / "map"
        / "transaction"
        / "hover"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    items = (
                        data.get("data", {})
                        .get("hoverDataList", [])
                    )

                    for item in items:

                        metrics = item.get(
                            "metric",
                            []
                        )

                        if not metrics:
                            continue

                        metric = metrics[0]

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "District": clean_name(
                                item.get(
                                    "name",
                                    ""
                                )
                            ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter": quarter_number(
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

    return pd.DataFrame(rows)


# ============================================================
# MAP USERS
# ============================================================

@st.cache_data
def load_map_users(data_root):

    path = (
        data_root
        / "map"
        / "user"
        / "hover"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    hover_data = (
                        data.get("data", {})
                        .get("hoverData", {})
                    )

                    for district, values in hover_data.items():

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "District": clean_name(
                                district
                            ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter": quarter_number(
                                file.name
                            ),
                            "Registered Users":
                                values.get(
                                    "registeredUsers",
                                    values.get(
                                        "registeredCount",
                                        0
                                    )
                                ),
                            "App Opens":
                                values.get(
                                    "appOpens",
                                    0
                                )
                        })

                except Exception:
                    continue

    return pd.DataFrame(rows)


# ============================================================
# TOP TRANSACTIONS
# ============================================================

@st.cache_data
def load_top_transactions(data_root):

    path = (
        data_root
        / "top"
        / "transaction"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    pincodes = (
                        data.get("data", {})
                        .get("pincodes", [])
                    )

                    for item in pincodes:

                        metric = item.get(
                            "metric",
                            {}
                        )

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "Pincode":
                                item.get(
                                    "entityName",
                                    ""
                                ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter":
                                quarter_number(
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

    return pd.DataFrame(rows)


# ============================================================
# TOP USERS
# ============================================================

@st.cache_data
def load_top_users(data_root):

    path = (
        data_root
        / "top"
        / "user"
        / "country"
        / "india"
        / "state"
    )

    rows = []

    if not path.exists():
        return pd.DataFrame()

    for state_dir in path.iterdir():

        if not state_dir.is_dir():
            continue

        for year_dir in state_dir.iterdir():

            if not year_dir.is_dir():
                continue

            for file in year_dir.glob("*.json"):

                try:

                    with open(
                        file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                    pincodes = (
                        data.get("data", {})
                        .get("pincodes", [])
                    )

                    for item in pincodes:

                        rows.append({
                            "State": clean_name(
                                state_dir.name
                            ),
                            "Pincode":
                                item.get(
                                    "name",
                                    ""
                                ),
                            "Year": int(
                                year_dir.name
                            ),
                            "Quarter":
                                quarter_number(
                                    file.name
                                ),
                            "Registered Users":
                                item.get(
                                    "registeredUsers",
                                    0
                                )
                        })

                except Exception:
                    continue

    return pd.DataFrame(rows)


# ============================================================
# LOAD ALL DATA
# ============================================================

with st.spinner(
    "Preparing PhonePe dashboard..."
):

    agg_transactions = load_aggregated_transactions(
        DATA_ROOT
    )

    agg_users = load_aggregated_users(
        DATA_ROOT
    )

    map_transactions = load_map_transactions(
        DATA_ROOT
    )

    map_users = load_map_users(
        DATA_ROOT
    )

    top_transactions = load_top_transactions(
        DATA_ROOT
    )

    top_users = load_top_users(
        DATA_ROOT
    )


# ============================================================
# VALIDATION
# ============================================================

if agg_transactions.empty:

    st.error(
        "No transaction data was found."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📱 PhonePe Pulse")

st.sidebar.markdown(
    "### Dashboard Filters"
)


states = sorted(
    agg_transactions["State"].unique()
)

years = sorted(
    agg_transactions["Year"].unique()
)

quarters = sorted(
    agg_transactions["Quarter"].unique()
)


selected_states = st.sidebar.multiselect(
    "State",
    states,
    default=states
)


selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)


selected_quarters = st.sidebar.multiselect(
    "Quarter",
    quarters,
    default=quarters
)


# ============================================================
# FILTER TRANSACTIONS
# ============================================================

ft = agg_transactions[
    agg_transactions["State"].isin(
        selected_states
    )
    &
    agg_transactions["Year"].isin(
        selected_years
    )
    &
    agg_transactions["Quarter"].isin(
        selected_quarters
    )
]


# ============================================================
# FILTER MAP DATA
# ============================================================

fm = map_transactions[
    map_transactions["State"].isin(
        selected_states
    )
    &
    map_transactions["Year"].isin(
        selected_years
    )
    &
    map_transactions["Quarter"].isin(
        selected_quarters
    )
] if not map_transactions.empty else pd.DataFrame()


# ============================================================
# HEADER
# ============================================================

st.title("📱 PhonePe Pulse Data Visualization")

st.markdown(
    "### Interactive analysis of PhonePe transactions, "
    "users, districts and top-performing locations."
)


# ============================================================
# KPI CARDS
# ============================================================

total_count = ft[
    "Transaction Count"
].sum()

total_amount = ft[
    "Transaction Amount"
].sum()

state_count = ft[
    "State"
].nunique()

year_count = ft[
    "Year"
].nunique()


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Transactions",
        f"{total_count:,.0f}"
    )


with c2:

    st.metric(
        "Transaction Value",
        f"₹{total_amount:,.2f}"
    )


with c3:

    st.metric(
        "States",
        state_count
    )


with c4:

    st.metric(
        "Years",
        year_count
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💳 Transactions",
        "👥 Users",
        "🗺️ Map / District",
        "🏆 Top Analysis",
        "📋 Data"
    ]
)


# ============================================================
# TAB 1 - TRANSACTIONS
# ============================================================

with tab1:

    st.subheader(
        "Transaction Analysis"
    )

    col1, col2 = st.columns(2)


    with col1:

        type_data = (
            ft.groupby(
                "Transaction Type"
            )[
                "Transaction Amount"
            ]
            .sum()
            .reset_index()
            .sort_values(
                "Transaction Amount",
                ascending=False
            )
        )

        fig = px.bar(
            type_data,
            x="Transaction Type",
            y="Transaction Amount",
            title="Transaction Amount by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        state_data = (
            ft.groupby("State")
            ["Transaction Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Transaction Amount",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            state_data,
            x="Transaction Amount",
            y="State",
            orientation="h",
            title="Top 10 States by Transaction Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Transaction Trend"
    )

    trend = (
        ft.groupby(
            ["Year", "Quarter"]
        )[
            "Transaction Amount"
        ]
        .sum()
        .reset_index()
    )

    trend["Period"] = (
        trend["Year"].astype(str)
        + " Q"
        + trend["Quarter"].astype(str)
    )

    fig = px.line(
        trend,
        x="Period",
        y="Transaction Amount",
        markers=True,
        title="Transaction Amount Over Time"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 2 - USERS
# ============================================================

with tab2:

    st.subheader(
        "User Analysis"
    )

    if agg_users.empty:

        st.warning(
            "User-by-device data is not available "
            "in this PhonePe data release."
        )

    else:

        fu = agg_users[
            agg_users["State"].isin(
                selected_states
            )
            &
            agg_users["Year"].isin(
                selected_years
            )
            &
            agg_users["Quarter"].isin(
                selected_quarters
            )
        ]

        user_brand = (
            fu.groupby("Brand")
            ["User Count"]
            .sum()
            .reset_index()
            .sort_values(
                "User Count",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            user_brand,
            x="Brand",
            y="User Count",
            title="Users by Device Brand"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            fu,
            use_container_width=True
        )


# ============================================================
# TAB 3 - MAP / DISTRICT
# ============================================================

with tab3:

    st.subheader(
        "State and District Analysis"
    )

    if fm.empty:

        st.warning(
            "Map transaction data is not available."
        )

    else:

        district_data = (
            fm.groupby("District")
            ["Transaction Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Transaction Amount",
                ascending=False
            )
            .head(20)
        )

        fig = px.bar(
            district_data,
            x="Transaction Amount",
            y="District",
            orientation="h",
            title="Top 20 Districts by Transaction Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        state_map = (
            fm.groupby("State")
            ["Transaction Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Transaction Amount",
                ascending=False
            )
        )

        fig = px.bar(
            state_map.head(20),
            x="State",
            y="Transaction Amount",
            title="State-wise Transaction Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.dataframe(
            fm,
            use_container_width=True
        )


# ============================================================
# TAB 4 - TOP ANALYSIS
# ============================================================

with tab4:

    st.subheader(
        "Top States / Pin Codes"
    )

    if top_transactions.empty:

        st.warning(
            "Top transaction data is not available."
        )

    else:

        ftp = top_transactions[
            top_transactions["State"].isin(
                selected_states
            )
            &
            top_transactions["Year"].isin(
                selected_years
            )
            &
            top_transactions["Quarter"].isin(
                selected_quarters
            )
        ]

        top_pin = (
            ftp.groupby("Pincode")
            ["Transaction Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Transaction Amount",
                ascending=False
            )
            .head(20)
        )

        fig = px.bar(
            top_pin,
            x="Transaction Amount",
            y="Pincode",
            orientation="h",
            title="Top 20 Pincodes by Transaction Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            ftp,
            use_container_width=True
        )


    st.subheader(
        "Top Registered Users"
    )

    if not top_users.empty:

        ftu = top_users[
            top_users["State"].isin(
                selected_states
            )
            &
            top_users["Year"].isin(
                selected_years
            )
            &
            top_users["Quarter"].isin(
                selected_quarters
            )
        ]

        top_user_pin = (
            ftu.groupby("Pincode")
            ["Registered Users"]
            .sum()
            .reset_index()
            .sort_values(
                "Registered Users",
                ascending=False
            )
            .head(20)
        )

        fig = px.bar(
            top_user_pin,
            x="Registered Users",
            y="Pincode",
            orientation="h",
            title="Top 20 Pincodes by Registered Users"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TAB 5 - DATA
# ============================================================

with tab5:

    st.subheader(
        "Aggregated Transaction Data"
    )

    st.dataframe(
        ft,
        use_container_width=True,
        height=500
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "PhonePe Pulse Dashboard | "
    "Python | Pandas | Plotly | Streamlit"
)
