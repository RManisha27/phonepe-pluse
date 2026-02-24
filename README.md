📊 PhonePe Transaction Insights Dashboard

📌 Project Overview

This project is an interactive data analytics dashboard built using Python and Streamlit to analyze PhonePe transaction data across India.

The dashboard visualizes transaction trends, registered users, district-level insights, brand usage, and category-based transaction distribution using SQL-powered data aggregation and Plotly visualizations.

🚀 Tech Stack

Python

Streamlit

SQLite

SQLAlchemy

Pandas

Plotly

📂 Features

🔹 Geo Analysis

State-wise transaction amount visualization

Year-wise and Quarter-wise filtering

Registered users distribution across states

🔹 Top Insights

Top 10 states by transaction amount

Top 10 districts by transaction volume

Top brands used for transactions

Category-wise transaction breakdown

Pincode-level analysis

🔹 Filter Insights

Year and quarter filtering

State and district-based analysis

Category-based transaction filtering

Brand usage analysis by state

📊 Key Insights

Maharashtra and Telangana lead in digital transaction volume.

Peer-to-peer transactions dominate overall transaction amount.

IT-driven urban districts show higher digital adoption.

Rural districts show comparatively lower transaction penetration.

🛠 Database Design

The project uses SQLite for structured storage of:

Aggregated Transactions

Map Transactions

Aggregated Users

Map Users

Top Transactions

Top Users

SQL aggregation and subqueries are used to generate analytical insights dynamically.

💡 Learning Outcomes

Advanced SQL (GROUP BY, Subqueries, Aggregations)

Interactive data visualization with Plotly

Streamlit dashboard development

Database integration with Python

Business insight generation from raw data

▶ How to Run Locally

pip install -r requirements.txt

streamlit run app.py




