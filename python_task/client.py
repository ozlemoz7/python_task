import os
import argparse
import requests
import pandas as pd
import datetime

# Define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keys', nargs='+', default=[], help='list of keys to include as extra columns')
parser.add_argument('-c', '--colored', action='store_true', help='color each row based on age of hu')
args = parser.parse_args()

# Read vehicle data from file
data = pd.read_csv('vehicles.csv')

# Authenticate with API
auth_url = 'https://api.baubuddy.de/index.php/login'
auth_payload = {'username': '365', 'password': '1'}
auth_headers = {
    'Authorization': 'Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz',
    'Content-Type': 'application/json'
}
auth_response = requests.post(auth_url, json=auth_payload, headers=auth_headers)
auth_response.raise_for_status()
access_token = auth_response.json()['oauth']['access_token']

# Get vehicle data from API
api_url = 'https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active'
api_headers = {'Authorization': f'Bearer {access_token}'}
api_response = requests.post(api_url, json=data.to_dict(orient='records'), headers=api_headers)
api_response.raise_for_status()
api_data = pd.DataFrame(api_response.json()['data'])

# Filter out resources without hu field
api_data = api_data.dropna(subset=['hu'])

# Resolve color codes for labelIds
if 'labelIds' in api_data.columns:
    label_id_url = 'https://api.baubuddy.de/dev/index.php/v1/labels/{}'
    color_codes = []
    for label_ids in api_data['labelIds']:
        if pd.isna(label_ids):
            color_codes.append('')
        else:
            label_id_list = [int(x) for x in label_ids.split(',')]
            label_colors = []
            for label_id in label_id_list:
                label_response = requests.get(label_id_url.format(label_id), headers=api_headers)
                label_response.raise_for_status()
                label_data = label_response.json()['data']
                if 'colorCode' in label_data and label_data['colorCode']:
                    label_colors.append(label_data['colorCode'])
            color_codes.append(','.join(label_colors))
    api_data['labelColors'] = color_codes

# Add extra columns based on input keys
if args.keys:
    for key in args.keys:
        if key in api_data.columns:
            data[key] = api_data[key]

# Color rows based on age of hu
if args.colored:
    today = pd.Timestamp.now().date()
    colors = []
    for index, row in api_data.iterrows():
        hu_date = pd.to_datetime(row['hu'], format='%Y-%m-%d').date()
        if (today - hu_date).days <= 90:
            colors.append('#007500')
        elif (today - hu_date).days <= 365:
            colors.append('#FFA500')
        else:
            colors.append('#b30000')
    api_data.style.apply(lambda x: f"background-color: {colors[x.name]}", axis=1)

# Sort rows by gruppe field
api_data = api_data.sort_values('gruppe')

# Create output
