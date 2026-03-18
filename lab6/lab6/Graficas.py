#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D  # necesario para 3D

def cargar_datos(nombre_archivo):
    data = np.loadtxt(nombre_archivo)

    # Asegurar formato Nx3
    if data.ndim == 1:
        if data.size % 3 != 0:
            raise ValueError(f"El archivo {nombre_archivo} no tiene datos múltiplos de 3.")
        data = data.reshape(-1, 3)

    # Si vino como 3xN, transponer
    if data.shape[0] == 3 and data.shape[1] != 3:
        data = data.T

    if data.shape[1] != 3:
        raise ValueError(f"El archivo {nombre_archivo} debe tener 3 columnas (x,y,z).")

    return data

def main():
    # Archivos
    archivo_actual = "xcurrent.txt"
    archivo_deseado = "xdesired.txt"

    # Cargar datos
    x_current = cargar_datos(archivo_actual)
    x_desired = cargar_datos(archivo_deseado)

    # Igualar longitud por seguridad
    n = min(len(x_current), len(x_desired))
    x_current = x_current[:n]
    x_desired = x_desired[:n]

    t = np.arange(n)

    # =========================
    # 1) Gráfica 3D
    # =========================
    fig1 = plt.figure(figsize=(8, 6))
    ax = fig1.add_subplot(111, projection='3d')

    ax.plot(x_current[:, 0], x_current[:, 1], x_current[:, 2], label='Posición actual')
    ax.plot(x_desired[:, 0], x_desired[:, 1], x_desired[:, 2], '--', label='Posición deseada')

    # Marcar inicio y fin
    ax.scatter(x_current[0, 0], x_current[0, 1], x_current[0, 2], marker='o', label='Inicio actual')
    ax.scatter(x_current[-1, 0], x_current[-1, 1], x_current[-1, 2], marker='^', label='Fin actual')
    ax.scatter(x_desired[0, 0], x_desired[0, 1], x_desired[0, 2], marker='s', label='Inicio deseado')
    ax.scatter(x_desired[-1, 0], x_desired[-1, 1], x_desired[-1, 2], marker='x', label='Fin deseado')

    ax.set_title('Espacio cartesiano 3D')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    ax.grid(True)

    # =========================
    # 2) Gráfica 2D de x, y, z
    # =========================
    fig2 = plt.figure(figsize=(10, 6))

    plt.plot(t, x_current[:, 0], label='x actual')
    plt.plot(t, x_desired[:, 0], '--', label='x deseada')

    plt.plot(t, x_current[:, 1], label='y actual')
    plt.plot(t, x_desired[:, 1], '--', label='y deseada')

    plt.plot(t, x_current[:, 2], label='z actual')
    plt.plot(t, x_desired[:, 2], '--', label='z deseada')

    plt.title('Cambio de posición cartesiana')
    plt.xlabel('Muestras')
    plt.ylabel('Posición')
    plt.legend()
    plt.grid(True)

    # Guardar imágenes
    fig1.savefig("grafica_3D.png", dpi=300, bbox_inches='tight')
    fig2.savefig("grafica_2D_xyz.png", dpi=300, bbox_inches='tight')

    plt.show()

# cd ~/lab_ws/src/lab6/lab6
# python3 Graficas.py

# antes fijar que tienes instalado numpy<2
# instala:

# python3 -m pip install "numpy<2" --user 
# python3 -c "import numpy; print(numpy.__version__)"
# Debería salir algo como 1.26.x.
# y vuelve # python3 Graficas.py


if __name__ == "__main__":
    main()