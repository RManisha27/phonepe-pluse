.PHONEPE TRANSCATION INSIGHTS

PhonePe Pulse Data Visualization and Exploration
Project Overview
This project aims to visualize and analyze PhonePe Pulse data to provide comprehensive insights into digital payment trends across India. By extracting, transforming, and loading data from the official PhonePe Pulse GitHub repository into a structured SQLite database, and then building an interactive Streamlit application, users can explore various metrics related to transactions and user engagement.

Features
Interactive Geospatial Visualizations: Explore transaction amounts and counts, and registered user data across Indian states and districts using interactive choropleth maps powered by Plotly.
Transaction Analysis: Detailed breakdowns of transaction amounts, counts, and types (e.g., peer-to-peer, merchant payments) across different years and quarters.
User Engagement Metrics: Analyze user brand distribution, registered user counts, and app open metrics.
Top Insights: Identify top 10 states, districts, and postal codes based on transaction volume, amount, and registered users.
Filtered Insights: Query specific states and districts to drill down into their transaction and user data over time.
User-Friendly Interface: An intuitive Streamlit web application for easy navigation and data exploration.
Technologies Used
Python: Programming language for data processing and application development.
Pandas: For data manipulation and cleaning.
SQLite: A lightweight, file-based database used for storing the processed data.
Streamlit: For building the interactive web application.
Plotly: For generating dynamic and interactive data visualizations, including choropleth maps and various charts.
SQLAlchemy: For connecting Python with the SQLite database.
pyngrok: To create a public URL for the local Streamlit application, making it accessible remotely.
Git: For version control and cloning the data repository.
Data Source
The data used in this project is sourced directly from the official PhonePe Pulse GitHub repository: https://github.com/PhonePe/pulse.git

Local Setup
To set up and run this project locally, follow these steps:

Clone the PhonePe Pulse Data Repository:

!git clone https://github.com/PhonePe/pulse.git
Install Required Python Packages:

!pip install pandas streamlit streamlit-option-menu sqlalchemy pyngrok
Prepare the SQLite Database: The notebook contains Python functions (agg_trans_data, agg_user_data, map_trans_data, map_user_data, top_trans_data, top_user_data) to extract data from the JSON files in the cloned pulse repository and load it into pandas DataFrames. These DataFrames are then saved as tables in a SQLite database named phonepe_data.db. Execute the relevant code cells in the provided notebook to create this database.

Example of database creation (assuming the data extraction functions are defined and executed):

import sqlite3
from sqlalchemy import create_engine

# Assuming the data extraction functions (e.g., agg_trans_data) are defined and run to create dataframes
# agg_trans_df = agg_trans_data()
# ... and so on for other dataframes

conn = sqlite3.connect('phonepe_data.db')
# Example: agg_trans_df.to_sql('aggregated_transactions', conn, if_exists='replace', index=False);
conn.commit()
conn.close()
Usage Guidelines
Run the Streamlit Application: Once the SQLite database is populated, you can run the Streamlit application. The streamlit_app.py file, which is generated in the notebook, contains the logic for the web application.

!streamlit run streamlit_app.py &> /dev/null &
Authenticate ngrok (if running in Colab/remote environment): To access your local Streamlit app via a public URL, you'll need to authenticate ngrok with your authtoken.

from pyngrok import ngrok
NGROK_AUTH_TOKEN = "YOUR_NGROK_AUTHTOKEN" # Replace with your actual ngrok authtoken
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
print("ngrok authenticated successfully!")
Get the Public URL: After ngrok authentication, open a tunnel to the Streamlit port (default is 8501).

from pyngrok import ngrok
public_url = ngrok.connect(addr="8501", proto="http")
print(f"Streamlit App URL: {public_url}")
