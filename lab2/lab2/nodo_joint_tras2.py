#!/usr/bin/env python3
import rclpy
import threading
import math
import xml.etree.ElementTree as ET
from sensor_msgs.msg import JointState

"""
Actividad 2.3


Para ejecutar el nodo pegar esta linea de code en una terminal despues de haber ejecutado 
la simulación en rviz

$ ros2 run lab2 nodo_joint_tras --ros-args -p q1:=-15.0 -p q2:=25.0 -p q3:=60.0

"""

def leer_angulos_desde_xml(ruta_xml):
    tree = ET.parse(ruta_xml)
    root = tree.getroot()

    q1_deg = float(root.find('q1').text)
    q2_deg = float(root.find('q2').text)
    q3_deg = float(root.find('q3').text)

    return q1_deg, q2_deg, q3_deg


def main():
    rclpy.init()

    node = rclpy.create_node('nodo_joint_tras')

    publisher = node.create_publisher(JointState, 'joint_states', 10)

    # Parámetro con la ruta del XML
    node.declare_parameter('angles_file', '')

    angles_file = str(node.get_parameter('angles_file').value)

    # Leer en grados desde XML
    q1_deg, q2_deg, q3_deg = leer_angulos_desde_xml(angles_file)

    # Convertir a radianes
    q1 = math.radians(q1_deg)
    q2 = math.radians(q2_deg)
    q3 = math.radians(q3_deg)

    node.get_logger().info(
        f'Valores leídos desde XML (grados): q1={q1_deg:.3f}, q2={q2_deg:.3f}, q3={q3_deg:.3f}'
    )
    node.get_logger().info(
        f'Convertidos a radianes: q1={q1:.3f}, q2={q2:.3f}, q3={q3:.3f}'
    )

    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    msg = JointState()
    rate = node.create_rate(10)

    while rclpy.ok():
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        msg.position = [q1, q2, q3, 0.0, 0.0, 0.0]

        publisher.publish(msg)
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()