import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator, handler: Handler, def_config: dict) -> None:
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
            "rotate": "false",
            "location_of_central_point": "(0, 0)",
            "meridian_point": "(90, -120)",
        }
        with open("config.json", "w") as config:
            json.dump(default_config, config, indent=4)

    def setDefaultConfig(self, config: dict) -> None:
        with open("config.json", "w") as c:
            json.dump(config, c, indent=4)

    def overrideDefaultConfigLocally(self, config: dict) -> dict:
        return config


    def getDefaultConfig(self) -> dict:
        with open("config.json", "r") as c:
            return json.load(c)

