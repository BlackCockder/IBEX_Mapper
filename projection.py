import matplotlib.pyplot as plt
import numpy as np

class Projection:
    def __init__(self):
        pass

    def projection(self, fig, ax, map_data):
        figure = plt.figure()
        plt.subplot(map_data, projection = "mollweide")
        plt.title(map_data.name)
        plt.grid(True)

        plt.show()




