from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
import numpy as np


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator

    def generateMapFromLink(self, link: str, accuracy: int) -> None:
        imported_data = np.loadtxt(link, comments='#')
        self.projection.projection(self.calculator.calculateMainFunctionFromData(imported_data, accuracy), accuracy)
