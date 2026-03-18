#!/usr/bin/env python3
import numpy as np

# elementos de una matriz
if __name__ == "__main__": # Indica que inicia el programa principal
 arreglo = np.array([1, 2, 3, 4, 5])
 print(arreglo[0]) # Acceder al primer elemento

 arreglo[2] = 10 # Modificar el tercer elemento
 print(arreglo)
 
 arreglo_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) # Acceder a una submatriz
 print(arreglo_2d[0, 1])
 print(arreglo_2d[1:, 1:])
