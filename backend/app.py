"""
This is the main file for the backend of the Sun Seekers app.
It contains the Flask application and the routes for the API.
"""
from datetime import datetime, timedelta
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize geocoder
geolocator = Nominatim(user_agent="sun_seekers")

@app.route('/api/search', methods=['POST'])
def search_location():
    "Function to search for a location and return the weather data"
    try:
        data = request.get_json()
        location = data.get('location')
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        # Geocode the location
        location_data = geolocator.geocode(location)
        if not location_data:
            return jsonify({'error': 'Location not found'}), 404

        # Get weather data (you'll need to implement this with your chosen weather API)
        weather_data = get_weather_data(location_data.latitude, location_data.longitude)
        return jsonify({
            'location': {
                'name': location_data.address,
                'latitude': location_data.latitude,
                'longitude': location_data.longitude
            },
            'weather': weather_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_weather_data(lat, lon):
    """Function to get the weather data for a location.
    
    Args:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location."""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return {'error': 'Weather API key not configured'}
    # Make API call to OpenWeatherMap
    url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt=7&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return {'error': 'Failed to fetch weather data'}
    data = response.json()
    # Process each day's data
    daily_forecast = []
    for day in data['list']:
        # Convert timestamp to readable date
        date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
        # Convert sunrise and sunset to readable time
        sunrise = datetime.fromtimestamp(day['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(day['sunset']).strftime('%H:%M')
        # Calculate sunny hours in hours
        sunny_hours = round((day['sunset'] - day['sunrise']) / 3600, 2)
        daily_forecast.append({
            'date': date,
            'temperature': round(day['temp']['day'], 2),
            'uv_index': round(day.get('uvi', 0), 2),
            'humidity': round(day['humidity'], 2),
            'sunny_hours': sunny_hours,
            'sunrise': sunrise,
            'sunset': sunset
        })
    return {
        'daily_forecast': daily_forecast
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Function to check the health of the backend.
    
    Returns:
        JSON: A response containing 'status': 'healthy' to indicate the backend is running
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
