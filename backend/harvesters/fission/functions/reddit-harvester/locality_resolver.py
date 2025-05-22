'''
Author: Zifei Li
Heavily modified by: Nemo Xiong
'''

import pandas as pd
import os
from collections import defaultdict
import pickle


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

output_dir = "final_locations"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def create_location_to_state_mapping(folder_path="locations_with_pid") -> tuple[dict, defaultdict, defaultdict]:
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
    if os.environ.get("FISSION_ENVIRONMENT"):
        folder_path = os.environ.get("FISSION_DEPLOY_DIR") + folder_path
    ambiguous_locations_pickle = os.path.join(output_dir, "ambiguous_locations.pkl")
    location_pids_pickle = os.path.join(output_dir, "location_pids.pkl")
    location_states_pickle = os.path.join(output_dir, "location_states.pkl")

    # Check if pickle files exist
    if (os.path.exists(ambiguous_locations_pickle) and 
        os.path.exists(location_pids_pickle) and 
        os.path.exists(location_states_pickle)):
        
        # Load from pickle files
        with open(ambiguous_locations_pickle, 'rb') as f:
            ambiguous_locations = pickle.load(f)
        
        with open(location_pids_pickle, 'rb') as f:
            location_pids = pickle.load(f)
            
        with open(location_states_pickle, 'rb') as f:
            location_states = pickle.load(f)
            
        return ambiguous_locations, location_pids, location_states
    
    else:
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
        
        for state, filename in state_files.items():
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                locality = row["Locality"].lower()
                location_states[locality].append(state)
                location_pids[locality].append(row['LOC_PID'])

        ambiguous_locations = {loc: states
                            for loc, states in location_states.items()
                            if len(states) > 1}

        # Save to pickle files
        with open(ambiguous_locations_pickle, 'wb') as f:
            pickle.dump(ambiguous_locations, f)
            
        with open(location_pids_pickle, 'wb') as f:
            pickle.dump(location_pids, f)
            
        with open(location_states_pickle, 'wb') as f:
            pickle.dump(location_states, f)

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