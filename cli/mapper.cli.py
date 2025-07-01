from ibex.calculator import Calculator
from ibex.configurator import Configurator
from ibex.app import IBEXMapper


def main() -> None:
    # Dodac projekcje
    calculator = Calculator()
    configurator = Configurator()

    mapper = IBEXMapper(calculator, configurator)
    print("IBEX Mapper")


if __name__ == "__main__":
    main()
