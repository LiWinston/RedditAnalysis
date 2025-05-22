'''
Author: Zifei Li
'''

import pandas as pd
import os

output_dir = 'locations with state and geographic coordinates'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def load_locality_data(state_code):
    '''
    Load LOCALITY data table to extract LOCALITY_NAME
    Geographical data is downloaded from: https://data.gov.au/data/dataset/geocoded-national-address-file-g-naf

    Arg:
        state_code (str): Abbreviation of the state

    Return:
        pd.DataFrame: DataFrame containing "LOCALITY_PID" and "LOCALITY_NAME" columns
    '''
    locality_file = f'G-NAF/Standard/{state_code}_LOCALITY_psv.psv'
    locality_df = pd.read_csv(locality_file, sep='|')
    locality_df = locality_df[['LOCALITY_PID', 'LOCALITY_NAME']]
    return locality_df

def load_locality_point_data(state_code):
    '''
    Load LOCALITY_POINT data table to extract LONGITUDE and LATITUDE
    Data source is the same as above
    We join the two tables using LOCALITY_PID as the key

    Arg:
        state_code (str): Abbreviation of the state

    Return:
        pd.DataFrame: DataFrame containing "LOCALITY_PID", "LONGITUDE", and "LATITUDE" columns
    '''
    locality_point_file = f'G-NAF/Standard/{state_code}_LOCALITY_POINT_psv.psv'
    locality_point_df = pd.read_csv(locality_point_file, sep='|')
    locality_point_df = locality_point_df[['LOCALITY_PID', 'LONGITUDE', 'LATITUDE']]
    return locality_point_df

def extract_locality_info(state_code):
    '''
    Load and merge locality and corresponding coordinate data based on the state code

    Arg:
        state_code (str): Abbreviation of the state

    Return:
        pd.DataFrame: DataFrame containing "Locality", "Longitude", "Latitude" columns
    '''
    locality_df = load_locality_data(state_code)
    locality_point_df = load_locality_point_data(state_code)

    merged_df = pd.merge(
        locality_df,
        locality_point_df,
        on='LOCALITY_PID',
        how='left'
    )

    result_df = merged_df[['LOCALITY_NAME', 'LONGITUDE', 'LATITUDE']]
    result_df = result_df.rename(columns={
        'LOCALITY_NAME': 'Locality',
        'LONGITUDE': 'Longitude',
        'LATITUDE': 'Latitude'
    })

    return result_df

def process_state(state_code):
    '''
    Process locality data by state code

    Arg:
        state_code (str): The abbreviation of the state

    Return:
        pd.DataFrame: DataFrame containing "Locality", "Longitude", and "Latitude" columns
    '''
    locality_info = extract_locality_info(state_code)

    csv_filename = f'{output_dir}/{state_code.lower()}_localities.csv'
    locality_info.to_csv(csv_filename, index=False)

    return locality_info

def main():
    state_codes = ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']

    all_localities_by_state = {}

    for state_code in state_codes:
        all_localities_by_state[state_code] = process_state(state_code)

    all_dfs = []

    for state_code, df in all_localities_by_state.items():
        df_copy = df.copy()
        df_copy['State'] = state_code
        all_dfs.append(df_copy)

    national_df = pd.concat(all_dfs)

    national_csv = f'{output_dir}/aus_all_localities.csv'
    national_df.to_csv(national_csv, index=False)

    return all_localities_by_state, national_df

if __name__ == "__main__":
    state_localities, national_localities = main()