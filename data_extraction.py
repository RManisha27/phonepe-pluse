import os
import json
import pandas as pd
import sqlite3


# ----------------------- AGGREGATED TRANSACTION -----------------------

def agg_trans_data():
    path = 'pulse/data/aggregated/transaction/country/india/state/'
    states = os.listdir(path)

    data_dict = {
        'state': [], 'year': [], 'quarter': [],
        'transaction_type': [], 'transaction_count': [],
        'transaction_amount': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for item in data['data']['transactionData']:
                    data_dict['state'].append(state)
                    data_dict['year'].append(year)
                    data_dict['quarter'].append(int(quarter.strip('.json')))
                    data_dict['transaction_type'].append(item['name'])
                    data_dict['transaction_count'].append(item['paymentInstruments'][0]['count'])
                    data_dict['transaction_amount'].append(item['paymentInstruments'][0]['amount'])

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    return df


# ----------------------- AGGREGATED USER -----------------------

def agg_user_data():
    path = "pulse/data/aggregated/user/country/india/state/"
    states = os.listdir(path)

    data_dict = {
        'state': [], 'year': [], 'quarter': [],
        'brand': [], 'user_count': [], 'percentage': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                try:
                    for item in data['data']['usersByDevice']:
                        data_dict['state'].append(state)
                        data_dict['year'].append(year)
                        data_dict['quarter'].append(int(quarter.strip('.json')))
                        data_dict['brand'].append(item['brand'])
                        data_dict['user_count'].append(item['count'])
                        data_dict['percentage'].append(item['percentage'])
                except:
                    pass

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    return df


# ----------------------- MAP TRANSACTION -----------------------

def map_trans_data():
    path = "pulse/data/map/transaction/hover/country/india/state/"
    states = os.listdir(path)

    data_dict = {
        'state': [], 'district': [], 'year': [],
        'quarter': [], 'transaction_count': [], 'transaction_amount': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for item in data['data']['hoverDataList']:
                    data_dict['state'].append(state)
                    data_dict['district'].append(item['name'])
                    data_dict['year'].append(year)
                    data_dict['quarter'].append(int(quarter.strip('.json')))
                    data_dict['transaction_count'].append(item['metric'][0]['count'])
                    data_dict['transaction_amount'].append(item['metric'][0]['amount'])

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    df['district'] = df['district'].str.replace("district", "").str.title()
    return df


# ----------------------- MAP USER -----------------------

def map_user_data():
    path = "pulse/data/map/user/hover/country/india/state/"
    states = os.listdir(path)

    data_dict = {
        'state': [], 'district': [], 'year': [],
        'quarter': [], 'registered_users': [], 'app_opens': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for district, values in data['data']['hoverData'].items():
                    data_dict['state'].append(state)
                    data_dict['district'].append(district)
                    data_dict['year'].append(year)
                    data_dict['quarter'].append(int(quarter.strip('.json')))
                    data_dict['registered_users'].append(values['registeredUsers'])
                    data_dict['app_opens'].append(values['appOpens'])

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    df['district'] = df['district'].str.replace("district", "").str.title()
    return df


# ----------------------- TOP TRANSACTION -----------------------

def top_trans_data():
    path = "pulse/data/top/transaction/country/india/state/"
    states = os.listdir(path)

    data_dict = {
        'state': [], 'pincode': [], 'year': [],
        'quarter': [], 'transaction_count': [], 'transaction_amount': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for item in data['data']['pincodes']:
                    data_dict['state'].append(state)
                    data_dict['pincode'].append(item['entityName'])
                    data_dict['year'].append(year)
                    data_dict['quarter'].append(int(quarter.strip('.json')))
                    data_dict['transaction_count'].append(item['metric']['count'])
                    data_dict['transaction_amount'].append(item['metric']['amount'])

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    return df


# ----------------------- TOP USER -----------------------

def top_user_data():
    path = "pulse/data/top/user/country/india/state/"
    states = os.listdir(path)

    data_dict = {
        'state': [], 'pincode': [], 'year': [],
        'quarter': [], 'registered_users': []
    }

    for state in states:
        state_path = path + state + "/"
        years = os.listdir(state_path)

        for year in years:
            year_path = state_path + year + "/"
            quarters = os.listdir(year_path)

            for quarter in quarters:
                file_path = year_path + quarter
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for item in data['data']['pincodes']:
                    data_dict['state'].append(state)
                    data_dict['pincode'].append(item['name'])
                    data_dict['year'].append(year)
                    data_dict['quarter'].append(int(quarter.strip('.json')))
                    data_dict['registered_users'].append(item['registeredUsers'])

    df = pd.DataFrame(data_dict)
    df['state'] = df['state'].str.replace("-", " ").str.title()
    return df


# ----------------------- CREATE DATABASE -----------------------

def create_database():
    conn = sqlite3.connect('phonepe_data.db')

    agg_trans_data().to_sql('aggregated_transactions', conn, if_exists='replace', index=False)
    agg_user_data().to_sql('aggregated_users', conn, if_exists='replace', index=False)
    map_trans_data().to_sql('map_transactions', conn, if_exists='replace', index=False)
    map_user_data().to_sql('map_users', conn, if_exists='replace', index=False)
    top_trans_data().to_sql('top_transactions', conn, if_exists='replace', index=False)
    top_user_data().to_sql('top_users', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    print("Database created successfully: phonepe_data.db")


# Run only if file executed directly
if __name__ == "__main__":
    create_database()