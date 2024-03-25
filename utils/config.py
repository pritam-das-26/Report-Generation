import os
import yaml

REQUIRED_CONFIG_SECTIONS = {
    "aws_path_configuration",
    "local_path_configuration",
}

class AppConfig:
    """
        Application Configuration class.

        Loads, validates, and manages the configuration from a YAML file.
    """
    def __init__(self, config_file_path):
        """
        Initialize the AppConfig.

        Args:
            config_file_path (str): The path to the configuration file.
        """
        self._config = self.load_config(config_file_path)
        self.validate_config()
        self.create_properties()

    @staticmethod
    def load_config(config_file_path):
        """
                Load the configuration from a YAML file.

                Args:
                    config_file_path (str): The path to the configuration file.

                Returns:
                    dict: The configuration dictionary.
        """
        try:
            print("you have entered here");
            with open(config_file_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error in YAML file structure: {exc}")


        aws_path = os.environ.get("AWS_PATH", "https://reportdemoimages.s3.amazonaws.com")
        PROJECT_NAME = os.environ.get("PROJECT_NAME", "demoproject")
        base_path=os.environ.get("BASE_PATH","")

        if not aws_path:
            raise ValueError("Base path is empty. Please set a valid base path as environment variable.")

        replacements = {
            "{AWS_PROJECT_PATH}": f"{aws_path}/{PROJECT_NAME}",
            "{BASE_PATH}": base_path,
        }

        def replace_path(item):
            if isinstance(item, dict):
                return {key: replace_path(value) for key, value in item.items()}
            elif isinstance(item, str):
                for placeholder, replacement in replacements.items():
                    item = item.replace(placeholder, replacement)
                return item
            else:
                return item

        return replace_path(config)

    def validate_config(self):
        """
         Validate the required configuration fields.

         Raises:
             ValueError: If any required configuration fields are missing.
         """
        for section in REQUIRED_CONFIG_SECTIONS:
            if section not in self._config:
                raise ValueError(f"Missing required configuration section: {section}")

    def create_properties(self):
        """
        Create properties for each configuration section.
        """
        for section in self._config:
            setattr(AppConfig, section, property(lambda self, sec=section: self.get_section(sec)))

    def get_section(self, section):
        """
           Get a configuration section.

           Args:
               section (str): The name of the configuration section.

           Returns:
               dict: The configuration section dictionary.

           Raises:
               ValueError: If the configuration section does not exist.
        """
        if section not in self._config:
            raise ValueError(f"Missing configuration section: {section}")
        return self._config.get(section, {})
