# Import libraries
from configparser import ConfigParser
from pathlib import Path


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parents[1]


def dict_config(config_db):
    section = 'postgresql'
    config_file_path = 'database_config/' + config_db
    if (len(config_file_path) > 0 and len(section) > 0):
        # Create an instance of ConfigParser class
        config_parser = ConfigParser()
        # Read the configuration file
        config_parser.read(config_file_path)
        # If the configuration file contains the provided section name
        if (config_parser.has_section(section)):
            # Read the options of the section
            config_params = config_parser.items(section)
            # Convert the list object to a python dictionary object
            # Define an empty dictionary
            db_conn_dict = {}
            # Loop in the list
            for config_param in config_params:
                # Get options key and value
                key = config_param[0]
                value = config_param[1]
                # Add the key value pair in the dictionary object
                db_conn_dict[key] = value
            # Get connection object use above dictionary object
            return db_conn_dict


def config(config_db="database.ini"):
    section = 'postgresql'
    config_file_path = 'database_config/' + config_db
    if (len(config_file_path) > 0 and len(section) > 0):
        # Create an instance of ConfigParser class
        config_parser = ConfigParser()
        # Read the configuration file
        config_parser.read(config_file_path)
        # If the configuration file contains the provided section name
        if (config_parser.has_section(section)):
            # Read the options of the section
            config_params = config_parser.items(section)
            # Convert the list object to a python dictionary object
            # Define an empty dictionary
            db_conn_string = ""
            # Loop in the list
            for config_param in config_params:
                # Join key and value to string
                db_conn_string = (
                    f'{db_conn_string} {config_param[0]} = {config_param[1]}')
            # Get connection object use above dictionary object
            return db_conn_string


if __name__ == "__main__":
    print(config("database.ini"))
