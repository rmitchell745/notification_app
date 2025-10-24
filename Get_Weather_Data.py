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
        url = f"http://api.openweathermap.org/data/2.5/forecast?zip={zipcode},cnt=3,us&appid={api_key}"
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


        if 'list' in data and data['list']:
            for forecast in data['list']:

                if 'dt_txt' in forecast and 'weather' in forecast and forecast['weather']:
                    date = forecast['dt_txt'].split()[0]
                    time = forecast['dt_txt'].split()[1]

                    if date not in human_readable_data[zipcode]:
                        human_readable_data[zipcode][date] = []


                    if 'description' in forecast['weather'][0]:
                        human_readable_data[zipcode][date].append(f"{time}: {forecast['weather'][0]['description']}")
                    else:
                        human_readable_data[zipcode][date].append(f"{time}: No description available")
                        logger.warning(f"No weather description available for {zipcode} at {date} {time}")
                else:
                     if zipcode not in human_readable_data:
                         human_readable_data[zipcode] = {}
                     if 'No forecast data available' not in human_readable_data[zipcode]:
                         human_readable_data[zipcode]['No forecast data available'] = ["No forecast data available for this time."]
                         logger.warning(f"Missing dt_txt or weather key for forecast in zipcode {zipcode}")


        else:

            human_readable_data[zipcode] = {"No forecast data available": ["No forecast data available for this zipcode."]}
            logger.warning(f"'list' key missing or empty in weather data for zipcode {zipcode}.")

    logger.info("Finished converting weather data to human readable format.")
    return human_readable_data


def generate_message(user, all_human_readable_data):
    message = f"Hello {user.name},\n\nHere is your weather forecast for the next 3 days:\n\n"
    logger.info(f"Generating message for user: {user.name}")
    # Iterate through the user's zipcodes
    for zipcode in user.zipcodes:

        if zipcode in all_human_readable_data:
            message += f"Weather for Zipcode {zipcode}:\n"
            user_weather_data = all_human_readable_data[zipcode]
            for date, forecasts in user_weather_data.items():
                message += f"Date: {date}\n"
                for forecast in forecasts:
                    message += f"{forecast}\n"
                message += "\n"
            logger.info(f"Included weather data for zipcode {zipcode} in message for {user.name}")
        else:
            message += f"No weather data available for Zipcode {zipcode}\n\n"
            logger.warning(f"No weather data available in human_readable_data for user {user.name}'s zipcode {zipcode}")

    logger.info(f"Message generated for user: {user.name}")
    return message
