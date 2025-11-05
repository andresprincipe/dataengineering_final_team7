#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import pandas as pd

# Creating dictionary of Maryland API endpoints
MD_API_DICT = {
    "md_air_enforcement": "https://opendata.maryland.gov/resource/fpps-g5hi.json",
    "md_water_enforcement": "https://opendata.maryland.gov/resource/qbwh-5vec.json",
}

CURRENT_DIR = os.getcwd()


def link_check(URL):
    """Checks if the API endpoint is reachable."""
    try:

        response = requests.get(URL)
        response.raise_for_status()

        return response.status_code
    
    except requests.exceptions.RequestException:

        return response.status_code


def fetch_data(URL):
    """
    Fetch data from the given URL
    and return it as a JSON object.
    """
    response = requests.get(URL)
    return response.json()

def get_all_file_paths(directory):
    """
    Retrieves a list of all absolute file paths within 
    a given directory.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            file_paths.append(full_path)
    return file_paths

if __name__ == "__main__":

    # create raw_data directory to store unprocessed data
    os.makedirs("raw_data",exist_ok=True)

    # iterate through the API dictionary and save data
    for data_name, api_url in MD_API_DICT.items():

        status_code = link_check(api_url)
        save_path = os.path.join(CURRENT_DIR, "raw_data", f"{data_name}.json")

        if status_code == 200:

            data = fetch_data(api_url)
            with open(save_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Data from {data_name} fetched and saved \
successfully.")

        else:

            print(
                f"Failed to reach the API endpoint for {data_name}. \
Status code: {status_code}"
            )
    
    # read in file paths from raw_data directory
    raw_data_path = os.path.join(CURRENT_DIR,'raw_data')
    file_paths = get_all_file_paths(raw_data_path)
    os.makedirs("clean_data",exist_ok=True) # make clean_data dir

    # iterate through file paths and read into DataFrames
    for path in file_paths:
        data_name = os.path.splitext(os.path.basename(path))[0]
        processed_path = os.path.join(CURRENT_DIR,
                                      "clean_data",
                                      f"{data_name}_cleaned.csv")
        if '.csv' in path:
            df = pd.read_csv(path)
            # add additional processing function/steps here
            df.to_csv(processed_path,index=False)
            print('Successfully processed:',data_name)

        elif '.json' in path:
            df = pd.read_json(path)
            # add additional processing function/steps here
            df.to_csv(processed_path,index=False)
            print('Successfully processed:',data_name)