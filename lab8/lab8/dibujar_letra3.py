#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

"""
Figura triangulo simulacion y pueba fisica 
"""

def quat_to_yaw(qx, qy, qz, qw):
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


def wrap_to_pi(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


# ---------- Variables globales (en lugar de la clase) ----------

cmd_pub = None
node = None

# (tipo, valor) -> tipo: 'orient' en grados, 'dist' en metros
# Letra L:
# (tipo, valor) -> tipo: 'orient' en grados, 'dist' en metros
# Triángulo equilátero:
secuencia = [
   # ('orient', 0.0),    # lado 1: orientar a 0°
    ('dist',   1.0),    # avanzar 1 m

    ('orient', 120.0),  # lado 2: orientar a 120°
    ('dist',   1.0),    # avanzar 1 m

    ('orient', 240.0),  # lado 3: orientar a 240° (equivale a -120°)
    ('dist',   1.0),    # avanzar 1 m
]

idx = 0           # paso actual de la secuencia
state_init = False

# Ganancias (reusamos lo de ctrl_distancia y ctrl_orientacion)
Kp_dist = 1
Kp_yaw  = 0.3

# Referencias internas para cada paso
d_ref = 0.0
yaw_ref = 0.0

# Variables para los pasos de distancia
x0 = None
y0 = None


def odom_callback(msg: Odometry):
    global idx, state_init, d_ref, yaw_ref, x0, y0
    global cmd_pub, node, secuencia, Kp_dist, Kp_yaw

    if idx >= len(secuencia):
        # Ya terminamos todos los pasos -> parar
        stop = Twist()
        cmd_pub.publish(stop)
        return

    tipo, valor = secuencia[idx]

    # Pose actual
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    q = msg.pose.pose.orientation
    yaw = quat_to_yaw(q.x, q.y, q.z, q.w)

    cmd = Twist()

    # --------- Paso de ORIENTACIÓN ---------
    if tipo == 'orient':
        if not state_init:
            yaw_ref = math.radians(valor)
            state_init = True
            node.get_logger().info(
                f'Paso {idx}: orientar a {valor:.1f} deg'
            )

        e = wrap_to_pi(yaw_ref - yaw)

        if abs(e) > math.radians(2):  # tolerancia 2°
            print('error: ' + str(e))
            w = Kp_yaw * e
            w_max = 1.82
            w = max(0.05, min(w, w_max))
            print('orientacion W: ' + str(w))
            cmd.angular.z = w
        else:
            # paso completado
            node.get_logger().info(
                f'   Orientación alcanzada: yaw ≈ {math.degrees(yaw):.1f} deg'
            )
            idx += 1
            state_init = False

    # --------- Paso de DISTANCIA ---------
    elif tipo == 'dist':
        if not state_init:
            d_ref = valor
            x0 = x
            y0 = y
            state_init = True
            node.get_logger().info(
                f'Paso {idx}: avanzar {d_ref:.2f} m'
            )

        dx = x - x0
        dy = y - y0
        d = math.sqrt(dx*dx + dy*dy)
        e = d_ref - d

        if e > 0.01:  # tolerancia 1 cm
            v = Kp_dist * e
            v_max = 0.26
            v = max(0.0, min(v, v_max))
            print(' didtancia V: ' + str(v))
            cmd.linear.x = v
        else:
            node.get_logger().info(
                f'   Distancia alcanzada: d={d:.3f} m (ref={d_ref:.3f} m)'
            )
            idx += 1
            state_init = False

    cmd_pub.publish(cmd)


def main(args=None):
    global cmd_pub, node

    rclpy.init(args=args)
    node = rclpy.create_node('dibujar_letra')

    cmd_pub = node.create_publisher(Twist, '/cmd_vel', 10)

    node.create_subscription(
        Odometry,
        '/odom',
        odom_callback,
        10
    )

    node.get_logger().info('Nodo dibujar_letra iniciado')

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
