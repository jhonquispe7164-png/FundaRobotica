#!/usr/bin/env python3
import rclpy                     # Librería principal de ROS2 en Python
import threading                 # Permite ejecutar procesos en paralelo
import random                    # Se usa para generar números aleatorios
from std_msgs.msg import Int32   # Tipo de mensaje entero de 32 bits

# ===== Variable global =====
# Aquí se guardará el número aleatorio generado en cada iteración.
numero_random = None

# ===== Función para generar número random (global) =====
def generar_numero():
    global numero_random
    # Genera un entero aleatorio entre 1 y 100
    # y lo guarda en la variable global.
    numero_random = random.randint(1, 100)

# ===== Nodo publicador: new_pubI =====
# Publica cada 1 segundo un entero (Int32) en el tópico "fake_sensorI"
def main():
    rclpy.init()
    # Se crea el nodo con nombre 'new_pubI'
    node = rclpy.create_node('new_pubI')

    # Se crea un publicador que enviará mensajes tipo Int32
    # por el tópico llamado 'fake_sensorI'
    publisher = node.create_publisher(Int32, 'fake_sensorI', 10)

    # Este hilo mantiene activo el procesamiento interno del nodo
    # mientras el programa principal sigue ejecutándose.
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    # Se crea un objeto mensaje del tipo Int32
    msg = Int32()

    # Se define la frecuencia de publicación:
    # 1 Hz significa una publicación cada segundo.
    rate = node.create_rate(1)

    while rclpy.ok():
        # En cada ciclo se genera un nuevo número aleatorio
        generar_numero()

        # El valor generado se coloca en el campo 'data' del mensaje
        msg.data = numero_random

        # Se publica el mensaje en el tópico
        publisher.publish(msg)

        # Se muestra en consola el número que se está enviando
        node.get_logger().info(f'Enviando número: {msg.data}')

        # Espera el tiempo necesario para mantener la frecuencia de 1 Hz
        rate.sleep()

    # Cuando ROS2 deja de ejecutarse, se destruye el nodo
    node.destroy_node()

    # Finalmente se cierra la comunicación de ROS2
    rclpy.shutdown()

if __name__ == '__main__':
    # Punto de entrada del programa
    main()