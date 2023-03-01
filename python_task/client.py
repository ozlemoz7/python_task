import argparse
import datetime
import pandas as pd
import requests

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keys', nargs='+', help='Additional columns to include in Excel file')
parser.add_argument('-c', '--colored', action='store_true', default=True, help='If True, color rows based on hu value')
args = parser.parse_args()

# Get current date in ISO format for Excel file name
current_date_iso_formatted = datetime.datetime.now().strftime('%Y-%m-%d')

# Read CSV file containing vehicle information
with open('vehicles.csv', 'r') as f:
    csv_data = f.read()

# Make POST request to server
headers = {'Content-type': 'text/csv', 'Authorization': 'Bearer bf427ec8a565621763c113b4a1e1dd9f52338e48'}
response = requests.post('https://api.baubuddy.de/dev/index.php/login', headers=headers, data=csv_data)

# Convert response data to pandas DataFrame and sort by gruppe column
response_json = response.json()
df = pd.DataFrame(response_json)
df = df.sort_values('gruppe')

# Define columns to include in Excel file
columns_to_include = ['rnr']
if args.keys is not None:
    columns_to_include += args.keys
if 'labelIds' in columns_to_include:
    columns_to_include.append('colorCode')
df = df[columns_to_include]

# Color rows based on hu value if -c flag is True
if args.colored:
    def color_row(row):
        if row['hu'] <= 3:
            return 'background-color: #007500'
        elif row['hu'] <= 12:
            return 'background-color: #FFA500'
        else:
            return 'background-color: #b30000'

    df = df.style.applymap(color_row, subset=pd.IndexSlice[:, ['hu']])

# Write DataFrame to Excel file
file_name = f'vehicles_{current_date_iso_formatted}.xlsx'
df.to_excel(file_name, index=False)
