import os
import json
import pandas as pd


BASE_PATH = "pulse/data"


def get_json_files(relative_path):
    """Get all JSON files from a PhonePe Pulse data folder."""
    path = os.path.join(BASE_PATH, relative_path)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Data folder not found: {path}\n"
            "Make sure the PhonePe Pulse repository is downloaded."
        )

    return path


# ---------------------------------------------------------
# AGGREGATED TRANSACTIONS
# ---------------------------------------------------------

def agg_trans_data():

    path = get_json_files(
        "aggregated/transaction/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                transactions = (
                    json_data.get("data", {})
                    .get("transactionData", [])
                )

                for item in transactions:

                    instrument = item.get(
                        "paymentInstruments", [{}]
                    )[0]

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "transaction_type": item.get("name"),
                        "transaction_count": instrument.get("count", 0),
                        "transaction_amount": instrument.get("amount", 0)
                    })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# AGGREGATED USERS
# ---------------------------------------------------------

def agg_user_data():

    path = get_json_files(
        "aggregated/user/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                users = (
                    json_data.get("data", {})
                    .get("usersByDevice", [])
                )

                for item in users:

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "brand": item.get("brand"),
                        "user_count": item.get("count", 0),
                        "percentage": item.get("percentage", 0)
                    })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# MAP TRANSACTIONS
# ---------------------------------------------------------

def map_trans_data():

    path = get_json_files(
        "map/transaction/hover/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                districts = (
                    json_data.get("data", {})
                    .get("hoverDataList", [])
                )

                for item in districts:

                    metric = item.get("metric", [{}])[0]

                    district = item.get("name", "")
                    district = district.replace(
                        "district", ""
                    ).strip().title()

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "district": district,
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "transaction_count": metric.get(
                            "count", 0
                        ),
                        "transaction_amount": metric.get(
                            "amount", 0
                        )
                    })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# MAP USERS
# ---------------------------------------------------------

def map_user_data():

    path = get_json_files(
        "map/user/hover/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                users = (
                    json_data.get("data", {})
                    .get("hoverData", {})
                )

                for district, values in users.items():

                    district = district.replace(
                        "district", ""
                    ).strip().title()

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "district": district,
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "registered_users": values.get(
                            "registeredUsers", 0
                        ),
                        "app_opens": values.get(
                            "appOpens", 0
                        )
                    })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# TOP TRANSACTIONS
# ---------------------------------------------------------

def top_trans_data():

    path = get_json_files(
        "top/transaction/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                pincodes = (
                    json_data.get("data", {})
                    .get("pincodes", [])
                )

                for item in pincodes:

                    metric = item.get("metric", {})

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "pincode": item.get("entityName"),
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "transaction_count": metric.get(
                            "count", 0
                        ),
                        "transaction_amount": metric.get(
                            "amount", 0
                        )
                    })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# TOP USERS
# ---------------------------------------------------------

def top_user_data():

    path = get_json_files(
        "top/user/country/india/state"
    )

    data = []

    for state in os.listdir(path):

        state_path = os.path.join(path, state)

        if not os.path.isdir(state_path):
            continue

        for year in os.listdir(state_path):

            year_path = os.path.join(state_path, year)

            if not os.path.isdir(year_path):
                continue

            for quarter_file in os.listdir(year_path):

                if not quarter_file.endswith(".json"):
                    continue

                file_path = os.path.join(
                    year_path,
                    quarter_file
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                pincodes = (
                    json_data.get("data", {})
                    .get("pincodes", [])
                )

                for item in pincodes:

                    data.append({
                        "state": state.replace("-", " ").title(),
                        "pincode": item.get("name"),
                        "year": int(year),
                        "quarter": int(
                            quarter_file.replace(".json", "")
                        ),
                        "registered_users": item.get(
                            "registeredUsers", 0
                        )
                    })

    return pd.DataFrame(data)
