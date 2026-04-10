# Weather Data Pipeline: DS5220 Project 2

## Data Source: Open-Meteo Weather API

This pipeline collects real-time weather data for New York City using the [Open-Meteo API](https://open-meteo.com/en/docs). Open-Meteo provides current conditions including temperature, wind speed, and weather codes. The API updates hourly, good for our scheduled data collection.

## Scheduled Application Process

The application runs as a Kubernetes CronJob on a K3s cluster deployed on AWS EC2. Every hour at minute 0 (UTC), the following process executes:

1. **Fetch Data** - Calls the Open-Meteo API to retrieve current weather for New York City (lat: 40.7128, lon: -74.0060)
2. **Persist Data** - Stores the timestamp, temperature (°C), windspeed (km/h), and weather code in a DynamoDB table (partition key: city, sort key: timestamp)
3. **Generate Visualization** - Queries all historical records and creates a time-series plot showing temperature trends
4. **Publish to S3** - Uploads both the updated plot (plot.png) and complete dataset (data.csv) to a public S3 website bucket

The pipeline runs autonomously in the cloud, collecting data 24/7 without requiring local execution.

## Output Data and Plot

### Data File (data.csv)
The CSV file contains all collected weather observations with the following schema:
- `city` - Location name (New York)
- `timestamp` - ISO 8601 UTC timestamp of the observation
- `temperature` - Air temperature in degrees Celsius
- `windspeed` - Wind speed in kilometers per hour
- `weathercode` - WMO weather interpretation code (e.g., 0=clear sky, 1=partly cloudy, 3=overcast)

### Plot (plot.png)
The visualization is a time-series line plot showing temperature trends over the collection period. The x-axis represents timestamp (chronological order), and the y-axis shows temperature in Celsius. Each data point is marked with a circle, and the line connects observations to show trends, daily cycles, and weather patterns.

## Repository Contents

- `weather_collector.py` - Main Python application
- `Dockerfile` - Container definition for the pipeline
- `requirements.txt` - Python dependencies

## Live Outputs

- **Temperature Plot:** http://ryp6vw-ds5220-weather.s3-website-us-east-1.amazonaws.com/plot.png
- **Complete Dataset:** http://ryp6vw-ds5220-weather.s3-website-us-east-1.amazonaws.com/data.csv

## Technologies Used

- **Kubernetes (K3s)** - Container orchestration
- **Docker** - Containerization
- **AWS EC2** - Compute host
- **AWS DynamoDB** - Data persistence
- **AWS S3** - Static website hosting
- **GitHub Container Registry** - Image storage
