#!/usr/bin/env python3
import numpy as np
# tipos de matrices 
if __name__ == "__main__": # Indica que inicia el programa principal
 arreglo_ceros = np.zeros(5) # Crear un arreglo de ceros
 print(arreglo_ceros)
 
 arreglo_unos = np.ones(5) # Crear un arreglo de unos
 print(arreglo_unos)

 arreglo_rango = np.arange(1, 10, 2) # Crear un arreglo con un rango de valores
 print(arreglo_rango)
 
 arreglo_espaciado = np.linspace(0, 1, 5) # Arreglo con valores espaciados uniformemente
 print(arreglo_espaciado)
