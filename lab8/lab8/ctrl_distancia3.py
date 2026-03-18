#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

# Variables globales - posiciones inciales 
x0 = None
y0 = None


reached = False
d_ref = 1.0     # metros
Kp = 0.8        # Ganancia proporcional Kp 


cmd_pub = None # aqui se guarda el publisher 
node = None 


# Define la función que se llamará cada vez que llegue un mensaje a /odom
def odom_callback(msg: Odometry):
    global x0, y0, reached, cmd_pub, node

    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y

    # Guardar la posición inicial en al inicio 
    if x0 is None:
        x0 = x
        y0 = y
        node.get_logger().info(
            f'Posición inicial registrada: x0={x0:.3f}, y0={y0:.3f}'
        )
        return

    # Distancia recorrida desde la posición inicial
    dx = x - x0
    dy = y - y0
    d = math.sqrt(dx*dx + dy*dy)

    # Error de distancia
    e = d_ref - d

    cmd = Twist()

    # Si todavía no llegó a la distancia deseada
    if e > 0.01:   # tolerancia de 1 cm
        v = Kp * e

        # Saturación de la velocidad para que no sea muy grande
        v_max = 0.3
        if v > v_max:
            v = v_max
        if v < 0.0:
            v = 0.0

        cmd.linear.x = v
        cmd.angular.z = 0.0
    else:
        # Ya llegó: detenerse
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        if not reached:
            node.get_logger().info(
                f'Distancia alcanzada. d={d:.3f} m (ref={d_ref:.3f} m)'
            )
            reached = True

    cmd_pub.publish(cmd)


def main(args=None):
    global cmd_pub, node

    rclpy.init(args=args)

    node = rclpy.create_node('ctrl_distancia')

    # Publisher de comandos de velocidad
    cmd_pub = node.create_publisher(Twist, '/cmd_vel', 10)

    # Suscriptor a la odometría
    node.create_subscription(
        Odometry,
        '/odom',
        odom_callback,
        10
    )

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Asegurar que el robot se detenga al cerrar el nodo
        stop_msg = Twist()
        cmd_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
