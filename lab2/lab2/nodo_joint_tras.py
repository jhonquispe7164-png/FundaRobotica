#!/usr/bin/env python3
import rclpy
import threading
import math
from sensor_msgs.msg import JointState

"""
Actividad 2.1, 2.2


Para ejecutar el nodo pegar esta linea de code en una terminal despues de haber ejecutado 
la simulación en rviz

$ ros2 run lab2 nodo_joint_tras --ros-args -p q1:=-15.0 -p q2:=25.0 -p q3:=60.0

"""

def main():
    rclpy.init()

    # Declarar el nombre del nodo
    node = rclpy.create_node('nodo_joint_tras')

    # Definir el publicador del tópico /joint_states
    publisher = node.create_publisher(JointState, 'joint_states', 10)

    # Declarar parámetros ROS de entrada
    node.declare_parameter('q1', 0.0)
    node.declare_parameter('q2', 0.0)
    node.declare_parameter('q3', 0.0)

    # Leer parámetros en grados
    q1_deg = float(node.get_parameter('q1').value)
    q2_deg = float(node.get_parameter('q2').value)
    q3_deg = float(node.get_parameter('q3').value)

    # Convertir de grados a radianes
    q1 = math.radians(q1_deg)
    q2 = math.radians(q2_deg)
    q3 = math.radians(q3_deg)

    node.get_logger().info(
        f'Valores recibidos en grados: q1={q1_deg}, q2={q2_deg}, q3={q3_deg}'
    )
    node.get_logger().info(
        f'Convertidos a radianes: q1={q1:.4f}, q2={q2:.4f}, q3={q3:.4f}'
    )

    node.get_logger().info(f'Valores recibidos: q1={q1:.4f}, q2={q2:.4f}, q3={q3:.4f}')

    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    # Definir una variable de tipo JointState
    msg = JointState()

    # Definir un bucle y su tiempo de muestreo
    rate = node.create_rate(10)   # 10 Hz

    while rclpy.ok():
        # Definir el tiempo en el stamp
        msg.header.stamp = node.get_clock().now().to_msg()

        # Definir los nombres de las articulaciones
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']

        # Definir las posiciones articulares
        msg.position = [q1, q2, q3, 0.0, 0.0, 0.0]

        # Publicar el mensaje
        publisher.publish(msg)

        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()