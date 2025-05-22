'''
Author: Zifei Li
'''

import pandas as pd
import re
import os

def update_csv_with_loc_pid(csv_file_path, geojson_file_path, output_file_path, state_code):
    """
    Read a CSV file, add LOC_PID column, and save as a new CSV file

    Args:
        csv_file_path (str): Path to the original CSV file
        geojson_file_path (str): Path to the geojson file
        output_file_path (str): Path to the output
        state_code (str): The abbreviation of the state
    """
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = pd.read_csv(csv_file_path)

    with open(geojson_file_path, 'r', encoding='utf-8') as f:
        geojson_text = f.read()

    loc_pid_pattern = r'"loc_pid"\s*:\s*"([^"]+)"'

    locality_field = f"{state_code.lower()}_loca_2"
    if state_code.lower() in ["act", "sa", "nt", "wa"]:
        locality_field = f"{state_code.lower()}_local_2"

    locality_pattern = fr'"{locality_field}"\s*:\s*"([^"]+)"'

    loc_pids = re.findall(loc_pid_pattern, geojson_text)
    localities = re.findall(locality_pattern, geojson_text)

    loc_pid_mapping = {}
    for i in range(min(len(localities), len(loc_pids))):
        loc_pid_mapping[localities[i]] = loc_pids[i]

    df['LOC_PID'] = df['Locality'].apply(
        lambda locality: find_loc_pid(locality, loc_pid_mapping)
    )

    columns = ['Locality', 'LOC_PID']
    for col in df.columns:
        if col not in ['Locality', 'LOC_PID']:
            columns.append(col)

    df = df[columns]

    df.to_csv(output_file_path, index=False)

def find_loc_pid(locality, mapping):
    """
    Find the corresponding LOC_PID for a given locality from the mapping

    Args:
        locality (str): The locality to find loc_pid
        mapping (dict): A dictionary mapping localities to loc_pid values

    Return:
        str: The corresponding LOC_PID
    """
    if not locality or pd.isna(locality):
        return ""

    if locality in mapping:
        return mapping[locality]

    upper_locality = locality.upper()
    for key in mapping:
        if str(key).upper() == upper_locality:
            return mapping[key]

    return ""

def main():
    csv_dir = "locations with state and geographic coordinates"
    geojson_dir = "geojson data"
    output_dir = "locations with pid"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    states = {
        "nsw": {
            "csv_file": "nsw_localities.csv",
            "geojson_file": "nsw_suburbs.geojson",
        },
        "act": {
            "csv_file": "act_localities.csv",
            "geojson_file": "act_suburbs.geojson",
        },
        "qld": {
            "csv_file": "qld_localities.csv",
            "geojson_file": "qld_suburbs.geojson",
        },
        "sa": {
            "csv_file": "sa_localities.csv",
            "geojson_file": "sa_suburbs.geojson",
        },
        "wa": {
            "csv_file": "wa_localities.csv",
            "geojson_file": "wa_suburbs.geojson",
        },
        "vic": {
            "csv_file": "vic_localities.csv",
            "geojson_file": "vic_suburbs.geojson",
        },
        "tas": {
            "csv_file": "tas_localities.csv",
            "geojson_file": "tas_suburbs.geojson",
        },
        "nt": {
            "csv_file": "nt_localities.csv",
            "geojson_file": "nt_suburbs.geojson",
        }
    }

    for state_code, files in states.items():

        csv_file = os.path.join(csv_dir, files["csv_file"])
        geojson_file = os.path.join(geojson_dir, files["geojson_file"])
        output_file = os.path.join(output_dir, f"{state_code}_localities_with_pid.csv")

        update_csv_with_loc_pid(csv_file, geojson_file, output_file, state_code)

if __name__ == "__main__":
    main()