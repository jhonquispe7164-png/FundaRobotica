#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class CtrlDistancia(Node):
    def __init__(self):
        super().__init__('ctrl_distancia')

        # Publisher de comandos de velocidad
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Suscriptor a la odometría
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Distancia deseada (puedes cambiarla)
        self.d_ref = 1.0    # metros
        # Ganancia proporcional
        self.Kp = 0.8

        # Posición inicial (se llenan con la primera lectura de odom)
        self.x0 = None
        self.y0 = None

        self.reached = False  # para saber si ya llegó

        #self.get_logger().info('Nodo ctrl_distancia iniciado')

    def odom_callback(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Guardar la posición inicial en la primera lectura
        if self.x0 is None:
            self.x0 = x
            self.y0 = y
            self.get_logger().info(
                f'Posición inicial registrada: x0={self.x0:.3f}, y0={self.y0:.3f}'
            )
            return

        # Distancia recorrida desde la posición inicial
        dx = x - self.x0
        dy = y - self.y0
        d = math.sqrt(dx*dx + dy*dy)

        # Error de distancia
        e = self.d_ref - d

        cmd = Twist()

        # Si todavía no llegó a la distancia deseada
        if e > 0.01:   # tolerancia de 1 cm
            v = self.Kp * e

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

            if not self.reached:
                self.get_logger().info(
                    f'Distancia alcanzada. d={d:.3f} m (ref={self.d_ref:.3f} m)'
                )
                self.reached = True

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CtrlDistancia()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Asegurar que el robot se detenga al cerrar el nodo
        stop_msg = Twist()
        node.cmd_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
