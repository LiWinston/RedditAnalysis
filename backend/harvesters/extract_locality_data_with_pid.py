'''
Author: Zifei Li
'''

import requests
import json
import os
import time

output_dir = "geojson data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Data source
download_urls = {
    "nsw": "https://data.gov.au/geoserver/nsw-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_91e70237_d9d1_4719_a82f_e71b811154c6&outputFormat=json",
    "act": "https://data.gov.au/geoserver/act-state-boundary-geoscape-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_83468f0c_313d_4354_9592_289554eb2dc9&outputFormat=json",
    "qld": "https://data.gov.au/geoserver/qld-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_6bedcb55_1b1f_457b_b092_58e88952e9f0&outputFormat=json",
    "sa": "https://data.gov.au/geoserver/sa-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bcfcfc9a_7c8d_479a_9bdf_b95ca66ad29a&outputFormat=json",
    "wa": "https://data.gov.au/geoserver/wa-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_6a0ec945_c880_4882_8a81_4dbcb85e74e5&outputFormat=json",
    "vic": "https://data.gov.au/geoserver/vic-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_af33dd8c_0534_4e18_9245_fc64440f742e&outputFormat=json",
    "tas": "https://data.gov.au/geoserver/tas-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_8bd7b6c1_1258_4df5_a98f_b6706e87de1e&outputFormat=json",
    "nt": "https://data.gov.au/geoserver/nt-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_12eca357_6bad_4130_9c47_eaaf4c11e039&outputFormat=json"
}

for state, url in download_urls.items():

    output_path = os.path.join(output_dir, f"{state}_suburbs.geojson")

    if os.path.exists(output_path):
        continue

    try:

        response = requests.get(url)

        if response.status_code == 200:
            try:
                json_data = response.json()
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f)
            except json.JSONDecodeError as e:
                print(f"Error in parsing json: {e}")

    except Exception as e:
        print(f"Error in downloading: {e}")

    time.sleep(3)