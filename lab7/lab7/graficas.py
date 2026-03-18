#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

# correr en la terminal nueva para cada caso los archivos
# mv ~/lab_ws/src/lab7/lab7/xactual.txt  ~/lab_ws/src/lab7/lab7/xactual_sub.txt
# mv ~/lab_ws/src/lab7/lab7/xdeseado.txt ~/lab_ws/src/lab7/lab7/xdeseado_sub.txt

# mv ~/lab_ws/src/lab7/lab7/xactual.txt  ~/lab_ws/src/lab7/lab7/xactual_crit.txt
# mv ~/lab_ws/src/lab7/lab7/xdeseado.txt ~/lab_ws/src/lab7/lab7/xdeseado_crit.txt

# mv ~/lab_ws/src/lab7/lab7/xactual.txt  ~/lab_ws/src/lab7/lab7/xactual_sobre.txt
# mv ~/lab_ws/src/lab7/lab7/xdeseado.txt ~/lab_ws/src/lab7/lab7/xdeseado_sobre.txt

"""
La idea es:
    - subamortiguado: llega más rápido pero con más oscilación
    - crítico: llega rápido y casi sin oscilar
    - sobreamortiguado: llega más lento y sin sobrepaso visible

    escalera para kd:
    valor pequeño
    valor medio
    valor grande
"""
def cargar_datos_xyz(nombre_archivo):
    data = np.loadtxt(nombre_archivo)

    if data.ndim == 1:
        data = data.reshape(1, -1)

    if data.shape[1] != 4:
        raise ValueError(
            f"El archivo {nombre_archivo} debe tener 4 columnas: t x y z"
        )

    t = data[:, 0]
    xyz = data[:, 1:4]
    return t, xyz


def graficar_caso(archivo_actual, archivo_deseado, titulo, nombre_salida):
    t_act, x_act = cargar_datos_xyz(archivo_actual)
    t_des, x_des = cargar_datos_xyz(archivo_deseado)

    n = min(len(t_act), len(t_des))
    t = t_act[:n]
    x_act = x_act[:n]
    x_des = x_des[:n]

    fig = plt.figure(figsize=(10, 6))

    plt.plot(t, x_act[:, 0], label='x actual')
    plt.plot(t, x_des[:, 0], '--', label='x deseada')

    plt.plot(t, x_act[:, 1], label='y actual')
    plt.plot(t, x_des[:, 1], '--', label='y deseada')

    plt.plot(t, x_act[:, 2], label='z actual')
    plt.plot(t, x_des[:, 2], '--', label='z deseada')

    plt.title(titulo)
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Posición [m]')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(nombre_salida, dpi=300, bbox_inches='tight')


def main():
    base = "/home/cristhian/lab_ws/src/lab7/lab7"

    # Caso 1: subamortiguado
    graficar_caso(
        f"{base}/xactual_sub.txt",
        f"{base}/xdeseado_sub.txt",
        "Evolución temporal del efector final - Caso subamortiguado",
        f"{base}/grafica_subamortiguado.png"
    )

    # Caso 2: críticamente amortiguado
    graficar_caso(
        f"{base}/xactual_crit.txt",
        f"{base}/xdeseado_crit.txt",
        "Evolución temporal del efector final - Caso críticamente amortiguado",
        f"{base}/grafica_critico.png"
    )

    # Caso 3: sobreamortiguado
    graficar_caso(
        f"{base}/xactual_sobre.txt",
        f"{base}/xdeseado_sobre.txt",
        "Evolución temporal del efector final - Caso sobreamortiguado",
        f"{base}/grafica_sobreamortiguado.png"
    )

    plt.show()


if __name__ == "__main__":
    main()