'''
Author: Zifei Li
'''

import pandas as pd
import os
from collections import defaultdict

# Dictionary of Australian location indicators
# Used to identify specific locations from text context and resolve place name ambiguity
state_indicators = {
    "VIC": ["victoria", "melbourne", "vic", "victorian"],
    "NSW": ["new south wales", "sydney", "nsw"],
    "QLD": ["queensland", "brisbane", "qld"],
    "WA": ["western australia", "perth", "wa"],
    "SA": ["south australia", "adelaide", "sa"],
    "TAS": ["tasmania", "hobart", "tas", "tasmanian"],
    "NT": ["northern territory", "darwin", "nt"],
    "ACT": ["australian capital territory", "canberra", "act"]
}

output_dir = "final locations"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_location_to_state_mapping(folder_path="locations with pid"):
    """
    Create a mapping dictionary of all Australian locations and their corresponding states.

    Arg:
        folder_path (str): Path to the folder containing location CSV files.

    Returns:
        ambiguous_locations (dict): A dictionary mapping localities that appear in multiple states
                                    to the list of those states
        location_pids (defaultdict(list)): A dictionary mapping localities to their corresponding PIDs
        location_states (defaultdict(list)): A dictionary mapping localities to their corresponding states
    """
    ambiguous_cache = os.path.join(output_dir, "ambiguous_locations.csv")
    master_table_cache = os.path.join(output_dir, "localities_master.csv")

    if os.path.exists(ambiguous_cache):
        ambiguous_df = pd.read_csv(ambiguous_cache)
        ambiguous_dict = {}

        for _, row in ambiguous_df.iterrows():
            location = row["locality"]
            states = row["states"].split(',')
            ambiguous_dict[location] = states

    state_files = {
        "ACT": "act_localities_with_pid.csv",
        "NSW": "nsw_localities_with_pid.csv",
        "NT": "nt_localities_with_pid.csv",
        "QLD": "qld_localities_with_pid.csv",
        "SA": "sa_localities_with_pid.csv",
        "TAS": "tas_localities_with_pid.csv",
        "VIC": "vic_localities_with_pid.csv",
        "WA": "wa_localities_with_pid.csv"
    }

    location_states = defaultdict(list)
    location_pids = defaultdict(list)
    master_data = []

    for state, filename in state_files.items():
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            locality = row["Locality"].lower()
            location_states[locality].append(state)
            location_pids[locality].append(row['LOC_PID'])
            master_entry = {
                'locality': row['Locality'],
                'loc_pid': row['LOC_PID'],
                'state': state
            }
            master_data.append(master_entry)

    ambiguous_locations = {loc: states
                           for loc, states in location_states.items()
                           if len(states) > 1}

    ambiguous_locations_list = []
    state_list = []
    for locality, states in ambiguous_locations.items():
        ambiguous_locations_list.append(locality)
        state_list.append(','.join(states))

    ambiguous_df = pd.DataFrame({
        'locality': ambiguous_locations_list,
        'states': state_list
    })

    ambiguous_df.to_csv(ambiguous_cache, index=False)

    if master_data:
        master_df = pd.DataFrame(master_data)
        master_df = master_df.sort_values(['state', 'locality']).reset_index(drop=True)
        master_df.to_csv(master_table_cache, index=False)

    return ambiguous_locations, location_pids, location_states

ambiguous_locations, location_pids, location_states = create_location_to_state_mapping()

def resolve_ambiguous_locations(text, location):
    """
       Try to resolve ambiguous location names

       Args:
           text (str): Text containing location names
           location (str): The location name to be resolved

       Return:
           str: Resolved location name, formatted as "location", "location|state", or "location (ambiguous locations)"
    """
    if location not in ambiguous_locations:
        return location

    possible_states = ambiguous_locations[location]
    text_lower = text.lower()
    text_with_space = f" {text_lower}"

    for state in possible_states:
        state_lower = state.lower()
        state_patterns = [f" {state_lower} ", f" {state_lower}'s"]
        for pattern in state_patterns:
            if pattern in text_with_space:
                return f"{location}|{state}"

        for indicator in state_indicators[state]:
            indicator_patterns = [f" {indicator} " , f" {indicator}'s"]
            for pattern in indicator_patterns:
                if pattern in text_with_space:
                    return f"{location}|{state}"

    return f'{location} (ambiguous locations)'