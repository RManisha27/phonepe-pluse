import sqlite3
from data_extraction import (
    agg_trans_data,
    agg_user_data,
    map_trans_data,
    map_user_data,
    top_trans_data,
    top_user_data
)


print("Starting PhonePe data extraction...")

print("1/6 Extracting aggregated transactions...")
agg_trans_df = agg_trans_data()
print(f"Rows: {len(agg_trans_df)}")

print("2/6 Extracting aggregated users...")
agg_user_df = agg_user_data()
print(f"Rows: {len(agg_user_df)}")

print("3/6 Extracting map transactions...")
map_trans_df = map_trans_data()
print(f"Rows: {len(map_trans_df)}")

print("4/6 Extracting map users...")
map_user_df = map_user_data()
print(f"Rows: {len(map_user_df)}")

print("5/6 Extracting top transactions...")
top_trans_df = top_trans_data()
print(f"Rows: {len(top_trans_df)}")

print("6/6 Extracting top users...")
top_user_df = top_user_data()
print(f"Rows: {len(top_user_df)}")


print("\nCreating SQLite database...")

conn = sqlite3.connect("phonepe_data.db")


agg_trans_df.to_sql(
    "aggregated_transactions",
    conn,
    if_exists="replace",
    index=False
)

agg_user_df.to_sql(
    "aggregated_users",
    conn,
    if_exists="replace",
    index=False
)

map_trans_df.to_sql(
    "map_transactions",
    conn,
    if_exists="replace",
    index=False
)

map_user_df.to_sql(
    "map_users",
    conn,
    if_exists="replace",
    index=False
)

top_trans_df.to_sql(
    "top_transactions",
    conn,
    if_exists="replace",
    index=False
)

top_user_df.to_sql(
    "top_users",
    conn,
    if_exists="replace",
    index=False
)


conn.commit()
conn.close()


print("\n===================================")
print("Database created successfully!")
print("File: phonepe_data.db")
print("===================================")
