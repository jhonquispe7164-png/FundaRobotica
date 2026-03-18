#!/usr/bin/env python3
import rclpy
from sensor_msgs.msg import JointState

def main():
    rclpy.init()

    # Crear nodo
    node = rclpy.create_node('new_node_joints')

    # Crear publicador en /joint_states
    publisher = node.create_publisher(JointState, 'joint_states', 10)
    
    # Frecuencia de publicación: 5 Hz
    rate = node.create_rate(5)

    msg = JointState()

    # Nombres de las articulaciones
    msg.name = ['pan_joint', 'tilt_joint']

    # Posiciones elegidas dentro del rango
    # pan_joint: entre -3.1 y 3.1
    # tilt_joint: entre -0.85 y 0.85
    msg.position = [0.5, 0.7] # cambiar ala posicion

    while rclpy.ok():
        # Tiempo actual del mensaje
        msg.header.stamp = node.get_clock().now().to_msg()

        # Publicar
        publisher.publish(msg)

        node.get_logger().info(
            'Publicando posiciones: pan_joint=%.2f, tilt_joint=%.2f'
            % (msg.position[0], msg.position[1])
        )

        rate.sleep()   # 10 Hz

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()