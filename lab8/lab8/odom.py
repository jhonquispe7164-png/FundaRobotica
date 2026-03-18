#!/usr/bin/env python3
import math
import csv
import os

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdomNode(Node):
    def __init__(self):
        super().__init__('odom')

        self.sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Ruta del archivo donde se guardará la trayectoria
        # (lo dejaré en el directorio actual desde donde ejecutes el nodo)
        self.filename = 'trayectoria.csv'

        # Abrir archivo y escribir cabecera
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['x', 'y', 'yaw_deg'])

        self.get_logger().info(f'Guardando datos en {os.path.abspath(self.filename)}')

    def odom_callback(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        qx, qy, qz, qw = q.x, q.y, q.z, q.w

        # Cuaternión -> yaw (rad)
        siny_cosp = 2.0 * (qw * qz + qx * qy)
        cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        yaw_deg = math.degrees(yaw)

        # Imprimir en pantalla
        self.get_logger().info(
            f'x = {x:.3f} m, y = {y:.3f} m, yaw = {yaw_deg:.1f} deg'
        )

        # Guardar en el archivo
        self.writer.writerow([x, y, yaw_deg])

    def destroy_node(self):
        # Cerrar bien el archivo al terminar
        self.file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
