#!/usr/bin/env python3
import time
import rclpy
from std_msgs.msg import Float64MultiArray

"""
Para ejecutar este nodo primero se debe cargar:
 $ ros2 launch lab3 robot_gz_control.launch 

y luego ejecutar este nodo:
 $ ros2 run lab3 new_send_joints
"""

def main():
    rclpy.init()

    # Declarar el nombre del nodo
    node = rclpy.create_node('JointsNode')

    # Definir el publicador para el tópico /forward_position_controller/commands
    publisher = node.create_publisher(
        Float64MultiArray,
        '/forward_position_controller/commands',
        10
    )

    # Pequeña pausa para asegurar que el publicador se conecte bien
    time.sleep(1.0)

    # Definir una variable de tipo Float64MultiArray
    msg = Float64MultiArray()

    # Primera configuración articular
    # pan_joint = -0.785, tilt_joint = 0.785
    msg.data = [-0.785, 0.785]
    node.get_logger().info(f'Enviando primera configuracion: {msg.data}')
    publisher.publish(msg)

    # Esperar 4 segundos
    time.sleep(4.0)

    # Segunda configuración articular
    # pan_joint = 0, tilt_joint = -0.785
    msg.data = [0.0, -0.785]
    node.get_logger().info(f'Enviando segunda configuracion: {msg.data}')
    publisher.publish(msg)

    # Pequeña espera para asegurar el envío
    time.sleep(1.0)

    node.get_logger().info('Movimiento finalizado.')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()