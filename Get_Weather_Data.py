import requests
import os
from Logger import logger

#use env variable for api keys, access openweather api for unique zipcodes and create a dictionary of 3 weather forecasts for each zipcode

api_key = os.environ.get('WEATHER_API_KEY')
if not api_key:
    logger.error("WEATHER_API_KEY environment variable not set.")
    exit() # Exit if no API key

def get_weather(uniq_zipcodes):
    weather_data = {}
    logger.info(f"Fetching weather data for {len(uniq_zipcodes)} unique zipcodes.")
    for zipcode in uniq_zipcodes:
        url = f"http://api.openweathermap.org/data/2.5/forecast?zip={zipcode},us&units=imperial&cnt=3&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            weather_data[zipcode] = data
            logger.info(f"Successfully fetched weather data for zipcode {zipcode}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for zipcode {zipcode}: {e}")
            weather_data[zipcode] = {"error": f"Could not fetch weather data: {e}"}

    return weather_data


def human_readable_weather(weather_data):
    human_readable_data = {}
    logger.info("Converting weather data to human readable format.")
    for zipcode, data in weather_data.items():
        human_readable_data[zipcode] = {}
        if "error" in data:
            human_readable_data[zipcode] = {"Error": [data["error"]]}
            logger.warning(f"Skipping human readable conversion for zipcode {zipcode} due to fetch error.")
            continue

        
        forecasts = data.get("list", [])

        if not forecasts :
            human_readable_data[zipcode] = {"No forecast data available": ["No forecast data available for this zipcode"]}
            continue

        for forecast in forecasts :
            dt = forecast.get("dt_txt", "")
            date, time = dt.split() if " " in dt else ("Unknown", "Unknown")

            temp = forecast.get("main", {}).get("temp","N/A")
            weather_info = forecast.get("weather",[{}])[0]
            main = weather_info.get("main", "N/A")
            desc = weather_info.get("description", "N/A")


            if date not in human_readable_data[zipcode]:
                human_readable_data[zipcode][date] = []
            
            forecast_line = f"{time}: Temp: {temp}F | {main} - {desc}"
            human_readable_data[zipcode][date].append(forecast_line)

            
    logger.info("Finished converting weather data to human readable format.")
    return human_readable_data


def generate_message(user, all_human_readable_data):
    message = f"Hello {user.name},\n\nHere is your weather forecast for the day:\n\n"
    logger.info(f"Generating message for user: {user.name}")
    # Iterate through the user's zipcodes
    for zipcode in user.zipcodes:

        message += f"Zipcode: {zipcode}\n"

        if zipcode in all_human_readable_data:
            user_weather_data = all_human_readable_data[zipcode]

            for date, forecasts in user_weather_data.items():
                message += f"Date: {date}\n"
                for forecast in forecasts:
                    message += f" - {forecast}\n"
                message += "\n"
            logger.info(f"Included weather data for zipcode {zipcode} in message for {user.name}")
        else:
            message += f"No weather data available for Zipcode {zipcode}\n\n"
            logger.warning(f"No weather data available in human_readable_data for user {user.name}'s zipcode {zipcode}")

    logger.info(f"Message generated for user: {user.name}")
    logger.info(message)
    return message
