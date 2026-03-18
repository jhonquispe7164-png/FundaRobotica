#!/usr/bin/env python3
import rclpy
import random
import time
from sensor_msgs.msg import Temperature

def main():
    rclpy.init()

    # Crear nodo
    node = rclpy.create_node('pub_sensor')

    # Crear publicador en el tópico "temp"
    publisher = node.create_publisher(Temperature, 'temp', 10)

    msg = Temperature()

    while rclpy.ok():
        temperatura_base = 22.0

        # Ruido aleatorio positivo o negativo
        if random.choice([True, False]):
            ruido = random.uniform(0.01, 0.5)
        else:
            ruido = random.uniform(-0.6, -0.02)

        msg.temperature = temperatura_base + ruido
        msg.variance = 0.0

        publisher.publish(msg)
        node.get_logger().info('Temperatura publicada: %.2f' % msg.temperature)

        time.sleep(0.2)   # 5 Hz

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()