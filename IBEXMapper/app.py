import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator, handler: Handler) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler

    def generateMapFromLink(self, link: str, accuracy: int, target_max_l: int, *config: dict) -> None:
        imported_data = np.loadtxt(link, comments='#')
        self.projection.projection(self.handler.processUserDataset(accuracy, target_max_l, imported_data), accuracy, link)

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

    def overrideDefaultConfigLocally(self, config: dict) -> None:
        pass
