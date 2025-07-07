import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np
from copy import deepcopy


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator, handler: Handler) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler
        self.generateDefaultConfig()
        self.def_config = self.getDefaultConfig()

    def generateMapFromLink(self, link: str, config=None) -> None:
        if config is None:
            config = self.def_config
        imported_data = np.loadtxt(link, comments='#')















    def generateDefaultConfig(self):
        default_config = {
            "map_accuracy": "720",
            "max_l_to_cache": "30",
            "rotate": "False",
            "location_of_central_point": "(0, 0)",
            "meridian_point": "(90, -120)",
        }
        with open("config.json", "w") as config:
            json.dump(default_config, config, indent=4)

    def setDefaultConfig(self, config: dict) -> None:
        with open("config.json", "w") as c:
            json.dump(config, c, indent=4)

    def generateConfigFromPartialInfo(self, partial_config: dict) -> dict:
        default_config = self.getDefaultConfig()

        merged_config = deepcopy(default_config)

        merged_config.update(partial_config)

        return merged_config

    def getDefaultConfig(self) -> dict:
        with open("config.json", "r") as config_file:
            return json.load(config_file)

    def resetConfig(self) -> None:
        self.generateDefaultConfig()
        self.def_config = self.getDefaultConfig()
