from calculator import Calculator
from configurator import Configurator
from projection import Projection

class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
