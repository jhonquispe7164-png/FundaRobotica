#!/usr/bin/env python3
import rclpy
import threading
from sensor_msgs.msg import JointState

def main():
    rclpy.init()

    # Declarar el nombre del nodo
    node = rclpy.create_node('JointsNode')

    # Definir el publicador del tópico /joint_states
    publisher = node.create_publisher(JointState, 'joint_states', 10)

    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    # Definir una variable de tipo JointState
    msg = JointState()



    # Definir un bucle y su tiempo de muestreo
    rate = node.create_rate(10)   # 10 Hz

    while rclpy.ok():
        # - Definir el tiempo en el stamp
        msg.header.stamp = node.get_clock().now().to_msg()

        # - Definir los nombres de la articulacion como una lista
        #   IMPORTANTE: reemplaza estos nombres por los de tu URDF
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']

        # - Definir las posiciones articulares como una lista
        #   Debe tener la misma cantidad de elementos que msg.name

        # Ingresa los valores
        msg.position = [-0.051, -0.527, 1.580, 0.527, 1.511, 0.00] # Valores de las articulaciones 

        # Publicar el mensaje
        publisher.publish(msg)

        
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()