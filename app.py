import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PhonePe Transaction Insights",
    page_icon="📱",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📱 PhonePe Transaction Insights")
st.markdown(
    "Interactive dashboard for exploring PhonePe transactions "
    "and user activity across India."
)


# =========================================================
# BASE DATA PATH
# =========================================================

BASE_PATH = "pulse/data"


# =========================================================
# CHECK DATA
# =========================================================

if not os.path.exists(BASE_PATH):

    st.error(
        "PhonePe Pulse data was not found."
    )

    st.info(
        "Make sure the `pulse` folder is present in your project."
    )

    st.code(
        "git clone https://github.com/PhonePe/pulse.git"
    )

    st.stop()


# =========================================================
# FUNCTION: LOAD AGGREGATED TRANSACTIONS
# =========================================================

@st.cache_data
def load_transactions():

    path = os.path.join(
        BASE_PATH,
        "aggregated",
        "transaction",
        "country",
        "india",
        "state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(
                state_path,
                year
            )

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    json_data = json.load(f)

                transactions = (
                    json_data
                    .get("data", {})
                    .get("transactionData", [])
                )

                for item in transactions:

                    instrument = item.get(
                        "paymentInstruments",
                        [{}]
                    )[0]

                    data.append({

                        "State":
                            state.replace(
                                "-",
                                " "
                            ).title(),

                        "Year":
                            int(year),

                        "Quarter":
                            int(
                                quarter_file
                                .replace(
                                    ".json",
                                    ""
                                )
                            ),

                        "Transaction Type":
                            item.get(
                                "name"
                            ),

                        "Transaction Count":
                            instrument.get(
                                "count",
                                0
                            ),

                        "Transaction Amount":
                            instrument.get(
                                "amount",
                                0
                            )
                    })

    return pd.DataFrame(data)


# =========================================================
# FUNCTION: LOAD AGGREGATED USERS
# =========================================================

@st.cache_data
def load_users():

    path = os.path.join(
        BASE_PATH,
        "aggregated",
        "user",
        "country",
        "india",
        "state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(
            path,
            state
        )

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(
                state_path,
                year
            )

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    json_data = json.load(f)

                users = (
                    json_data
                    .get("data", {})
                    .get("usersByDevice", [])
                )

                for item in users:

                    data.append({

                        "State":
                            state.replace(
                                "-",
                                " "
                            ).title(),

                        "Year":
                            int(year),

                        "Quarter":
                            int(
                                quarter_file
                                .replace(
                                    ".json",
                                    ""
                                )
                            ),

                        "Brand":
                            item.get(
                                "brand"
                            ),

                        "User Count":
                            item.get(
                                "count",
                                0
                            ),

                        "Percentage":
                            item.get(
                                "percentage",
                                0
                            )
                    })

    return pd.DataFrame(data)


# =========================================================
# LOAD DATA
# =========================================================

with st.spinner(
    "Loading PhonePe data..."
):

    transaction_df = load_transactions()
    user_df = load_users()


# =========================================================
# CHECK DATA
# =========================================================

if transaction_df.empty:

    st.error(
        "Transaction data could not be loaded."
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🔎 Filters")


# State filter

states = sorted(
    transaction_df["State"].unique()
)

selected_states = st.sidebar.multiselect(
    "Select State",
    states,
    default=states
)


# Year filter

years = sorted(
    transaction_df["Year"].unique()
)

selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)


# Quarter filter

quarters = sorted(
    transaction_df["Quarter"].unique()
)

selected_quarters = st.sidebar.multiselect(
    "Select Quarter",
    quarters,
    default=quarters
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_transactions = transaction_df[
    transaction_df["State"].isin(
        selected_states
    )
    &
    transaction_df["Year"].isin(
        selected_years
    )
    &
    transaction_df["Quarter"].isin(
        selected_quarters
    )
]


filtered_users = user_df[
    user_df["State"].isin(
        selected_states
    )
    &
    user_df["Year"].isin(
        selected_years
    )
    &
    user_df["Quarter"].isin(
        selected_quarters
    )
]


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📊 Key Performance Indicators")


total_transactions = filtered_transactions[
    "Transaction Count"
].sum()


total_amount = filtered_transactions[
    "Transaction Amount"
].sum()


total_users = filtered_users[
    "User Count"
].sum()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Transactions",
        f"{total_transactions:,.0f}"
    )


with col2:

    st.metric(
        "Total Transaction Amount",
        f"₹{total_amount:,.2f}"
    )


with col3:

    st.metric(
        "Total Users",
        f"{total_users:,.0f}"
    )


# =========================================================
# TRANSACTION TYPE ANALYSIS
# =========================================================

st.subheader(
    "💳 Transaction Type Analysis"
)


transaction_type = (
    filtered_transactions
    .groupby("Transaction Type")
    ["Transaction Amount"]
    .sum()
    .reset_index()
    .sort_values(
        "Transaction Amount",
        ascending=False
    )
)


fig1 = px.bar(
    transaction_type,
    x="Transaction Type",
    y="Transaction Amount",
    title="Transaction Amount by Type"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# =========================================================
# STATE ANALYSIS
# =========================================================

st.subheader(
    "🇮🇳 State-wise Transaction Analysis"
)


state_data = (
    filtered_transactions
    .groupby("State")
    .agg(
        {
            "Transaction Count": "sum",
            "Transaction Amount": "sum"
        }
    )
    .reset_index()
    .sort_values(
        "Transaction Amount",
        ascending=False
    )
)


fig2 = px.bar(
    state_data.head(10),
    x="State",
    y="Transaction Amount",
    title="Top 10 States by Transaction Amount"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# =========================================================
# TRANSACTION TREND
# =========================================================

st.subheader(
    "📈 Transaction Trend"
)


trend = (
    filtered_transactions
    .groupby(
        ["Year", "Quarter"]
    )
    ["Transaction Amount"]
    .sum()
    .reset_index()
)


trend["Period"] = (
    trend["Year"].astype(str)
    + " Q"
    + trend["Quarter"].astype(str)
)


fig3 = px.line(
    trend,
    x="Period",
    y="Transaction Amount",
    markers=True,
    title="Transaction Amount Over Time"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# =========================================================
# USER BRAND ANALYSIS
# =========================================================

st.subheader(
    "📱 User Brand Analysis"
)


brand_data = (
    filtered_users
    .groupby("Brand")
    ["User Count"]
    .sum()
    .reset_index()
    .sort_values(
        "User Count",
        ascending=False
    )
)


fig4 = px.pie(
    brand_data.head(10),
    names="Brand",
    values="User Count",
    title="User Distribution by Device Brand"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# =========================================================
# DATA TABLE
# =========================================================

st.subheader(
    "📋 Transaction Data"
)

st.dataframe(
    filtered_transactions,
    use_container_width=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "PhonePe Transaction Insights | "
    "Python • Pandas • Plotly • Streamlit"
)
