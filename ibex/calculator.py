from scipy.special import sph_harm as spherical_harmonics
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, dpi):
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2*np.pi, dpi))
        heatmapData = np.zeros((dpi, dpi), dtype=np.complex128)
        i = 0
        for row in data:
            l = row[0].astype(int)
            m = row[1].astype(int)
            coeff = row[2]
            Y_lm = spherical_harmonics(m, l, longitude, colatitude)
            heatmapData += coeff * Y_lm
            i += 1
            print(f"Calculating... {round((i/data.shape[0]) * 100, 2)}%")
        return heatmapData.real

    def cashing(self, data):
        data_types = [np.int32, np.int32, np.float64, np.float64]

        saved_calculations = np.zeros(l.size, dtype=data_types)

        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))

        for i in range(l):
            for j in range(-i, i):




        saved_calculations_array = np.array(saved_calculations)
        np.savetxt("cashing.txt", saved_calculations_array, delimiter=",")