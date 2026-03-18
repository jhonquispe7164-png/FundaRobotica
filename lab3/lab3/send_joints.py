#!/usr/bin/env python3
import time
import rclpy
from std_msgs.msg import Float64MultiArray

"""
Para ejecutar este nodo primero se debe de cargar:
 $ ros2 launch lab3 robot_gz_control.launch 

 y luego ejecutar este nodo:

 $ ros2 run lab3 send_joints

"""

def main():
    rclpy.init()

    # Declarar el nombre del nodo
    node = rclpy.create_node('JointsNode')

    # Definir el publicador para el tópico /forward_position_controller/commands
    # Tipo de mensaje: std_msgs/msg/Float64MultiArray
    publisher = node.create_publisher(
        Float64MultiArray,
        '/forward_position_controller/commands',
        10
    )

    # Pequeña pausa para asegurar que el publicador se conecte bien
    time.sleep(1.0)

    # Definir una variable de tipo Float64MultiArray
    msg = Float64MultiArray()

    # Definir las propiedades de la variable
    # data[0] -> pan_joint
    # data[1] -> tilt_joint

    # Definir la lógica del código para que se mueva de una posición a otra
    posiciones = [
        [0.0, 0.0],
        [0.5, 0.5],
        [-0.5, 0.3],
        [0.8, -0.4],
        [0.0, 0.0]
    ]

    for pos in posiciones:
        msg.data = pos
        node.get_logger().info(f'Enviando posiciones: {msg.data}')
        publisher.publish(msg)
        time.sleep(2.0)

    node.get_logger().info('Movimiento finalizado.')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()