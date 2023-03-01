import csv
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/vehicles', methods=['POST'])
def vehicles():
    # Parse CSV file from request
    csv_data = request.files['file'].read().decode('utf-8')
    reader = csv.DictReader(csv_data.splitlines())

    # Retrieve active vehicles from API
    response = requests.get('https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active')
    active_vehicles = response.json()

    # Merge CSV data with active vehicles
    vehicles = {}
    for vehicle in active_vehicles:
        vehicles[vehicle['rnr']] = vehicle
    for row in reader:
        vehicles[row['rnr']] = row

    # Filter out vehicles with no hu value
    vehicles = {k: v for k, v in vehicles.items() if v.get('hu')}

    # Resolve colorCode for each labelId
    label_colors = {}
    for vehicle in vehicles.values():
        for label_id in vehicle.get('labelIds', []):
            if label_id not in label_colors:
                label_response = requests.get(f'https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}')
                label_colors[label_id] = label_response.json()['colorCode']

    # Return data as JSON
    return jsonify({'vehicles': vehicles, 'labelColors': label_colors})
