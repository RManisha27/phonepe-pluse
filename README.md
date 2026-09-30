# 💜 PhonePe Transaction Insights
https://phonepe-pluse-nnkrjgp2dvszqcawcjbgfo.streamlit.app/

A Streamlit dashboard built on the [PhonePe Pulse](https://github.com/PhonePe/pulse) dataset, covering transactions, user engagement, and insurance across India — down to state, district, and pincode level.

**Pipeline:** PhonePe Pulse JSON → SQL (9 tables) → SQL analysis → Plotly charts → Streamlit dashboard

## Features

- **Overview** — headline metrics (transaction count, payment value, average ticket size, registered users, insurance policies)
- **Transactions** — category-wise breakdown, top states by value
- **Users** — device brand share, app engagement (opens per user) by state
- **Insurance** — policy trends by year, top states and districts
- **Geo Map** — animated India choropleth with multiple colour themes, top-10 leaderboard, and district-level treemap drill-down
- **Top Performers** — top 10 states / districts / pincodes by any metric
- **Business Case Studies** — 10 ready-made SQL queries with charts, covering growth trends, seasonality, segmentation, and outlier detection
- Year and quarter filters apply across every page

## Tech stack

Python · Streamlit · Pandas · Plotly · SQLAlchemy · SQLite (or MySQL / PostgreSQL)

## Project structure
