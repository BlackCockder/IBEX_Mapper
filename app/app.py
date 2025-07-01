from calculator import Calculator
from configurator import Configurator


class IBEXMapper:
    def __init__(self, projection, calculator: Calculator, configurator: Configurator) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
