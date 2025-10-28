import os
import yaml
import os
from Logger import logger # Import the logger

#this module when called loads a dictionary from a yaml configuration file using a relational path and generates singleton classes for use in the other .py modules

def load_config():
  cwd = os.getcwd()

  config_path = os.path.join(cwd,"Config",'weather_config.yml')

  try:
      with open(config_path, 'r') as file:
          config = yaml.safe_load(file)
          logger.info(f"Config file loaded successfully from {config_path}")
  except FileNotFoundError:
      logger.error(f"Error: Config file not found at {config_path}")
      return None # Return None if config loading fails


  return config # Return the config dictionary


#weather_config.yml consists of a dictionary for email settings for use with smtplib and a users dictionary containing a list with a dictionary for each user





class User:
    def __init__(self, name, ph_nmbr, carrier, zipcodes):
        self.name = name
        self.ph_nmbr = ph_nmbr
        self.carrier = carrier
        self.zipcodes = zipcodes
        logger.info(f"User object created for {self.name}")


# now to finish configuration and initialization we need to return a list of User Instances and a list of unique zipcodes

def Load_users(config):
  user_list = []
  # Check if 'users' key exists in config and is a list
  if config and 'users' in config and isinstance(config['users'], list):
      logger.info("Loading users from config.")
      for user in config['users']:
          # Add checks for expected keys in user dictionary
          if isinstance(user, dict) and 'name' in user and 'ph_nmbr' in user and 'carrier' in user and 'zipcodes' in user and isinstance(user['zipcodes'], list):
              name = user['name']
              ph_nmbr = user['ph_nmbr']
              carrier = user['carrier']
              zipcodes = user['zipcodes']
              user_instance = User(name, ph_nmbr, carrier, zipcodes)
              user_list.append(user_instance)
              logger.info(f"Loaded user: {name}")
          else:
              logger.warning(f"Skipping invalid user entry in config: {user}")
  elif config:
      logger.warning("'users' key not found or not a list in config file.")

  logger.info(f"Finished loading {len(user_list)} users.")
  return user_list

def Load_zipcodes(user_list):
  zipcodes = []
  for user in user_list :
      for zipcode in user.zipcodes:
          zipcodes.append(zipcode)

  uniq_zipcodes = list(set(zipcodes))
  logger.info(f"Found {len(uniq_zipcodes)} unique zipcodes.")

  return uniq_zipcodes
