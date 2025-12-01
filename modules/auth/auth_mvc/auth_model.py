import yaml


class AuthModel:
    def __init__(self):
        config = self._load_config() # Load configuration from YAML file


    def _load_config(self):
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)

            return config
        
        except FileNotFoundError:
            print("Configuration file not found.")
            return {}
        
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return {}
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {}