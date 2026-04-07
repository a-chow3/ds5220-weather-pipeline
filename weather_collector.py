#!/usr/bin/env python3
import boto3
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timezone
from decimal import Decimal

# Configuration
CITY = "New York"
LAT = 40.7128
LON = -74.0060
TABLE_NAME = "weather-tracking"
S3_BUCKET = "ryp6vw-ds5220-weather"

def get_weather():
    """Fetch current weather from Open-Meteo"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_to_dynamodb(data):
    """Save weather data to DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(TABLE_NAME)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Convert floats to Decimal for DynamoDB
    item = {
        'city': CITY,
        'timestamp': timestamp,
        'temperature': Decimal(str(data['current_weather']['temperature'])),
        'windspeed': Decimal(str(data['current_weather']['windspeed'])),
        'weathercode': Decimal(str(data['current_weather']['weathercode']))
    }
    
    table.put_item(Item=item)
    print(f"Saved: {timestamp} | Temp: {data['current_weather']['temperature']}°C")
    return item

def query_history():
    """Get all weather history for the city"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(TABLE_NAME)
    
    response = table.query(
        KeyConditionExpression='city = :city',
        ExpressionAttributeValues={':city': CITY}
    )
    
    items = response.get('Items', [])
    # Convert Decimal back to float for plotting
    for item in items:
        if 'temperature' in item:
            item['temperature'] = float(item['temperature'])
        if 'windspeed' in item:
            item['windspeed'] = float(item['windspeed'])
    
    items.sort(key=lambda x: x['timestamp'])
    return items

def generate_plot(history):
    """Generate temperature trend plot"""
    if len(history) < 2:
        print("Not enough data for plot yet")
        return None
    
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    plt.figure(figsize=(12, 6))
    sns.set_style("darkgrid")
    
    plt.plot(df['timestamp'], df['temperature'], marker='o', linewidth=2, markersize=4)
    plt.title(f'Temperature Trend - {CITY}', fontsize=14)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_path = '/tmp/plot.png'
    plt.savefig(plot_path)
    plt.close()
    
    return plot_path

def upload_to_s3(file_path, s3_key):
    """Upload file to S3 bucket"""
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.upload_file(file_path, S3_BUCKET, s3_key, ExtraArgs={'ContentType': 'image/png'})
    print(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")

def save_csv_to_s3(history):
    """Save history as CSV to S3"""
    if not history:
        return
    
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Drop any non-serializable columns
    df = df[['city', 'timestamp', 'temperature', 'windspeed', 'weathercode']]
    
    csv_path = '/tmp/data.csv'
    df.to_csv(csv_path, index=False)
    
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.upload_file(csv_path, S3_BUCKET, 'data.csv', ExtraArgs={'ContentType': 'text/csv'})
    print(f"Uploaded CSV to s3://{S3_BUCKET}/data.csv")

def main():
    print(f"Weather Pipeline Run - {datetime.now(timezone.utc).isoformat()}")
    
    weather_data = get_weather()
    save_to_dynamodb(weather_data)
    
    history = query_history()
    print(f"Total records: {len(history)}")
    
    plot_path = generate_plot(history)
    if plot_path:
        upload_to_s3(plot_path, 'plot.png')
    
    save_csv_to_s3(history)

if __name__ == "__main__":
    main()
