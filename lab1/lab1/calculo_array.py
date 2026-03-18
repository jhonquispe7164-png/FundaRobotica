#!/usr/bin/env python3
import numpy as np

# cálculos con matrices
if __name__ == "__main__": # Indica que inicia el programa principal
 # Producto de matrices
 matriz1 = np.array([[1, 2], [3, 4]])
 matriz2 = np.array([[5, 6], [7, 8]])
 producto = np.dot(matriz1, matriz2)
 print(producto) # [[19 22]
                 # [43 50]]
