import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import numpy as np

# Read CSV file
df = pd.read_csv('parking availability.csv', header=None)

# Parse data
data_records = []
current_date = None

for idx, row in df.iterrows():
    # Detect a date row
    if pd.notna(row[1]) and isinstance(row[1], str) and '2025' in str(row[1]):
        date_str = row[1]
        # Parse date string like "Thursday, September 25, 2025"
        try:
            date_obj = datetime.strptime(date_str, "%A, %B %d, %Y")
            current_date = date_obj.strftime("%Y-%m-%d")  # Convert to ISO format YYYY-MM-DD
        except:
            continue
    
    # Detect a data row (has space type and location)
    if pd.notna(row[1]) and current_date and row[1] in ['A', 'B', 'D', 'S', 'SR', 'Visitor']:
        space_type = row[1]
        location = row[3]
        
        # Ensure location is valid and not a header
        if pd.notna(location) and location not in ['Location', '']:
            try:
                # Extract values for four time slots
                time_8am = pd.to_numeric(row[4], errors='coerce')
                time_10am = pd.to_numeric(row[5], errors='coerce')
                time_12pm = pd.to_numeric(row[6], errors='coerce')
                time_2pm = pd.to_numeric(row[7], errors='coerce')
                
                data_records.append({
                    'date': current_date,
                    'space_type': space_type,
                    'location': location,
                    '8:00 AM': time_8am,
                    '10:00 AM': time_10am,
                    '12:00 PM': time_12pm,
                    '2:00 PM': time_2pm
                })
            except:
                continue

# Convert to DataFrame
data_df = pd.DataFrame(data_records)

print(f"Total records parsed: {len(data_df)}")
print(f"Number of dates: {data_df['date'].nunique()}")
print(f"Number of locations: {data_df['location'].nunique()}")
print(f"Number of space types: {data_df['space_type'].nunique()}")
print(f"\nSpace Types: {sorted(data_df['space_type'].unique())}")
print(f"\nSample data:")
print(data_df.head(10))

# Gather all unique (location, space_type) combinations
locations = sorted(data_df['location'].unique())
space_types = sorted(data_df['space_type'].unique())

print(f"\nWill generate {len(locations)} × {len(space_types)} = {len(locations) * len(space_types)} chart combinations")

# Build dictionary for all charts
charts_data = {}

for location in locations:
    for space_type in space_types:
        # Filter data for the current location and space type
        subset = data_df[(data_df['location'] == location) & 
                        (data_df['space_type'] == space_type)].copy()
        
        if len(subset) > 0:
            # Sort by date
            subset = subset.sort_values('date')
            
            key = f"{location}_{space_type}"
            
            # Convert NaN to None (null in JSON)
            def convert_nan(value):
                if pd.isna(value) or (isinstance(value, float) and np.isnan(value)):
                    return None
                return value
            
            charts_data[key] = {
                'location': location,
                'space_type': space_type,
                'dates': subset['date'].tolist(),
                '8:00 AM': [convert_nan(v) for v in subset['8:00 AM'].tolist()],
                '10:00 AM': [convert_nan(v) for v in subset['10:00 AM'].tolist()],
                '12:00 PM': [convert_nan(v) for v in subset['12:00 PM'].tolist()],
                '2:00 PM': [convert_nan(v) for v in subset['2:00 PM'].tolist()]
            }

print(f"\nChart combinations with data: {len(charts_data)}")

# Save JSON for HTML consumption
with open('parking_data.json', 'w') as f:
    json.dump(charts_data, f, indent=2)

print("\nData saved to parking_data.json")
