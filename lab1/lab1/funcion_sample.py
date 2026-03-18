#!/usr/bin/env python3
def saludar(nombre):
 mensaje = "Hola, " + nombre
 return mensaje

#el main
if __name__ == "__main__": # Indica que inicia el programa principal
 saludo = saludar("Mundo_Cristhian") # Llamado a la funcion
 print(saludo) # Impresion del resultado de la funcion
