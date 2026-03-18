#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def quat_to_yaw(qx, qy, qz, qw):
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


def wrap_to_pi(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


class DibujaLetra(Node):
    def __init__(self):
        super().__init__('dibujar_letra')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # ---------- SECUENCIA DE LA LETRA ----------
        # (tipo, valor) -> tipo: 'orient' en grados, 'dist' en metros
        # Letra L:
        self.secuencia = [
            ('orient', 0.0),   # orientar a 0°
            ('dist',   1.0),   # avanzar 1 m
            ('orient', -90.0), # girar a -90°
            ('dist',   0.5),   # avanzar 0.5 m
        ]
        # -------------------------------------------

        self.idx = 0           # paso actual de la secuencia
        self.state_init = False

        # Ganancias (reusamos lo de ctrl_distancia y ctrl_orientacion)
        self.Kp_dist = 0.8
        self.Kp_yaw  = 1.5

        # Referencias internas para cada paso
        self.d_ref = 0.0
        self.yaw_ref = 0.0

        # Variables para los pasos de distancia
        self.x0 = None
        self.y0 = None

        self.get_logger().info('Nodo dibujar_letra iniciado')

    def odom_callback(self, msg: Odometry):
        if self.idx >= len(self.secuencia):
            # Ya terminamos todos los pasos -> parar
            stop = Twist()
            self.cmd_pub.publish(stop)
            return

        tipo, valor = self.secuencia[self.idx]

        # Pose actual
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        yaw = quat_to_yaw(q.x, q.y, q.z, q.w)

        cmd = Twist()

        # --------- Paso de ORIENTACIÓN ---------
        if tipo == 'orient':
            if not self.state_init:
                self.yaw_ref = math.radians(valor)
                self.state_init = True
                self.get_logger().info(
                    f'Paso {self.idx}: orientar a {valor:.1f} deg'
                )

            e = wrap_to_pi(self.yaw_ref - yaw)

            if abs(e) > math.radians(2.0):  # tolerancia 2°
                w = self.Kp_yaw * e
                w_max = 1.0
                w = max(-w_max, min(w, w_max))
                cmd.angular.z = w
            else:
                # paso completado
                self.get_logger().info(
                    f'   Orientación alcanzada: yaw ≈ {math.degrees(yaw):.1f} deg'
                )
                self.idx += 1
                self.state_init = False

        # --------- Paso de DISTANCIA ---------
        elif tipo == 'dist':
            if not self.state_init:
                self.d_ref = valor
                self.x0 = x
                self.y0 = y
                self.state_init = True
                self.get_logger().info(
                    f'Paso {self.idx}: avanzar {self.d_ref:.2f} m'
                )

            dx = x - self.x0
            dy = y - self.y0
            d = math.sqrt(dx*dx + dy*dy)
            e = self.d_ref - d

            if e > 0.01:  # tolerancia 1 cm
                v = self.Kp_dist * e
                v_max = 0.3
                v = max(0.0, min(v, v_max))
                cmd.linear.x = v
            else:
                self.get_logger().info(
                    f'   Distancia alcanzada: d={d:.3f} m (ref={self.d_ref:.3f} m)'
                )
                self.idx += 1
                self.state_init = False

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = DibujaLetra()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
