#!/usr/bin/env python3
import rclpy
import threading
import random
from std_msgs.msg import Float64

# Variable global para guardar el número random
numero_random = None

def generar_numero():
    global numero_random
    # Número float aleatorio (puedes ajustar el rango si tu profe dijo otro)
    numero_random = random.uniform(0.0, 100.0)

def main():
    rclpy.init()
    node = rclpy.create_node('new_pubF')                 # nombre del nodo
    publisher = node.create_publisher(Float64, 'fake_sensorF', 10)  # tópico y tipo

    # Hilo para manejar callbacks (mismo estilo que el anterior)
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    msg = Float64()
    rate = node.create_rate(1)   # 1 Hz -> una vez por segundo

    while rclpy.ok():
        generar_numero()         # actualiza la variable global
        msg.data = numero_random
        publisher.publish(msg)
        node.get_logger().info(f'fake_sensorF publishing: {msg.data}')
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

