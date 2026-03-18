#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def quat_to_yaw(qx, qy, qz, qw):
    """Convierte cuaternión a yaw (rad)."""
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


def wrap_to_pi(angle):
    """Envuelve un ángulo a [-pi, pi]."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


class CtrlOrientacion(Node):
    def __init__(self):
        super().__init__('ctrl_orientacion')

        # Publicador de comandos de velocidad
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Suscriptor a /odom
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )


        # --- Parámetros del control ---
        # Orientación deseada (rad): aquí 90° = pi/2
        self.yaw_ref = math.radians(180)
        # Ganancia proporcional
        self.Kp = 1.5

        self.reached = False

        self.get_logger().info(
            f'Nodo ctrl_orientacion iniciado. '
            f'Yaw deseado = {math.degrees(self.yaw_ref):.1f} deg'
        )

    def odom_callback(self, msg: Odometry):
        # Obtener yaw actual desde cuaternión
        q = msg.pose.pose.orientation
        yaw = quat_to_yaw(q.x, q.y, q.z, q.w)

        # Error de orientación
        e = wrap_to_pi(self.yaw_ref - yaw)

        cmd = Twist()

        # Tolerancia: 2 grados
        if abs(e) > math.radians(2.0):
            w = self.Kp * e

            # Saturación de velocidad angular
            w_max = 1.0   # rad/s
            if w > w_max:
                w = w_max
            if w < -w_max:
                w = -w_max

            cmd.angular.z = w
            cmd.linear.x = 0.0
        else:
            # Ya alcanzó la orientación deseada
            cmd.angular.z = 0.0
            cmd.linear.x = 0.0
            if not self.reached:
                self.get_logger().info(
                    f'Orientación alcanzada. '
                    f'Yaw ≈ {math.degrees(yaw):.1f} deg'
                )
                self.reached = True

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CtrlOrientacion()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Asegurar que se detenga al cerrar
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
