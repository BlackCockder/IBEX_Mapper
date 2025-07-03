from ibex.calculator import Calculator
from ibex.configurator import Configurator
from ibex.app import IBEXMapper
from ibex.projection import Projection
import time


def main() -> None:
    projection = Projection()
    calculator = Calculator()
    configurator = Configurator()

    mapper = IBEXMapper(projection, calculator, configurator)
    mapper.generateMapFromLink("testcase.txt", 100)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
