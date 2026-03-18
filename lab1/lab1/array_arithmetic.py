#!/usr/bin/env python3
import numpy as np

# Operaciones matematicas con matrices 
if __name__ == "__main__": # Indica que inicia el programa principal
 arreglo1 = np.array([1, 2, 3])
 arreglo2 = np.array([4, 5, 6])

 # Suma
 print("Suma",arreglo1 + arreglo2) # [5 7 9]

 # Resta
 print("Resta",arreglo1 - arreglo2) # [-3 -3 -3]

 # Multiplicación
 print("Multiplicacion",arreglo1 * arreglo2) # [ 4 10 18]
 
 # División
 print("Division",arreglo1 / arreglo2) # [0.25 0.4 0.5 ]
