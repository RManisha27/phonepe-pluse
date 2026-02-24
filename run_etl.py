from data_extraction import *
import sqlite3

# Run extraction functions
agg_trans_df = agg_trans_data()
agg_user_df = agg_user_data()
map_trans_df = map_trans_data()
map_user_df = map_user_data()
top_trans_df = top_trans_data()
top_user_df = top_user_data()

# Create database
conn = sqlite3.connect("phonepe_data.db")

agg_trans_df.to_sql("aggregated_transactions", conn, if_exists="replace", index=False)
agg_user_df.to_sql("aggregated_users", conn, if_exists="replace", index=False)
map_trans_df.to_sql("map_transactions", conn, if_exists="replace", index=False)
map_user_df.to_sql("map_users", conn, if_exists="replace", index=False)
top_trans_df.to_sql("top_transactions", conn, if_exists="replace", index=False)
top_user_df.to_sql("top_users", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Database created successfully ✅")
