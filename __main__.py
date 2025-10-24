import Load_Config
import Send_Email_SMS
import Get_Weather_Data
import smtplib
import yaml
import os
from Logger import logger

#main python module that is scheduled to run.

logger.info("Application started.")

#first load config

config = Load_Config.load_config()

# Check if config load was successful
if config is None:
    logger.error("Configuration loading failed. Exiting.")
    exit() # Exit if config is not loaded
else:
    logger.info("Configuration loaded successfully.")


# Call the functions from Load_Config to get the user data and unique zipcodes
user_list = Load_Config.Load_users(config)
uniq_zipcodes = Load_Config.Load_zipcodes(user_list)

# Check if user_list or uniq_zipcodes are empty and handle accordingly
if not user_list:
    logger.error("No users loaded. Exiting.")
    exit()
else:
    logger.info(f"Loaded {len(user_list)} users.")

if not uniq_zipcodes:
    logger.error("No unique zipcodes found. Exiting.")
    exit()
else:
    logger.info(f"Found {len(uniq_zipcodes)} unique zipcodes.")


# Initialize EmailConfig
try:
    email_config = Send_Email_SMS.EmailConfig.get_instance(config.get('email_settings')) # Pass only email settings from config
    if not hasattr(email_config, '_initialized') or not email_config._initialized:
        logger.error("Email configuration initialization failed. Cannot send emails.")

        email_sending_possible = False
    else:
        logger.info("Email configuration initialized successfully.")
        email_sending_possible = True

except ValueError as e:
    logger.error(f"Error initializing EmailConfig: {e}")
    email_sending_possible = False # Cannot send emails if initialization fails


#Generate the Weather Data
weather_data = Get_Weather_Data.get_weather(uniq_zipcodes)
human_readable_data = Get_Weather_Data.human_readable_weather(weather_data)

# Check if weather_data is successfully retrieved
if not weather_data:
    logger.error("Failed to retrieve weather data. Exiting.")
    exit()
else:
    logger.info("Weather data retrieved successfully.")


#generate the messages
messages = {} # Store messages as a dictionary with user as key
logger.info("Generating messages for users.")
for user in user_list:
    message = Get_Weather_Data.generate_message(user, human_readable_data)
    messages[user] = message # Associate to user

logger.info("Finished generating messages.")

#send the messages
if email_sending_possible:
    logger.info("Attempting to send messages.")
    try:
        # Establish SSL context and login
        smtp_server = email_config.smtp_server
        smtp_port = email_config.smtp_port
        sender_email = email_config.sender_email
        sender_password = email_config.sender_password

        # Define carrier_sms_protocols
        #Can move to config ayaml eventually
        carrier_sms_protocol = {
            "AT&T": "txt.att.net",
            "Boost Mobile": "sms.myboostmobile.com",
            "Cricket": "sms.mycricket.com",
            "Verizon": "vtext.com",
            "T-Mobile": "tmomail.net"
        }


        with smtplib.SMTP_SSL(smtp_server, smtp_port) as ssl_context:
            logger.info("SMTP SSL context established.")
            ssl_context.login(sender_email, sender_password)
            logger.info("SMTP login successful.")

            for user, message_body in messages.items():
                # Check if message_body is not empty
                if message_body and message_body.strip() != f"Hello {user.name},\n\nHere is your weather forecast for the next 3 days:\n\n":
                    logger.info(f"Sending message to {user.name}")
                    # Call send_email
                    Send_Email_SMS.send_email(ssl_context, sender_email, user.ph_nmbr, user.carrier, "Weather Update", message_body, carrier_sms_protocol)
                else:
                    logger.warning(f"Skipping sending message to {user.name} due to empty or incomplete message.")

    except Exception as e:
        logger.error(f"An error occurred during the email sending process: {e}")
else:
    logger.warning("Skipping email sending due to configuration errors.")

logger.info("Application finished.")
