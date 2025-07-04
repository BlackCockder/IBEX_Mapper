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

    def generateMapFromLink(self, link: str, accuracy: int, target_max_l: int) -> None:
        imported_data = np.loadtxt(link, comments='#')
        self.projection.projection(self.handler.processUserDataset(accuracy, target_max_l, imported_data), accuracy, link)
