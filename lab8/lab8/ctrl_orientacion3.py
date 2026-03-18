#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("ctrl_orientacion")
    pub = node.create_publisher(Twist, "/cmd_vel", 10)

    # Parámetros
    yaw_ref = math.radians(90.0)
    Kp = 1.5
    tol_rad = math.radians(1.0)
    time.sleep(1.0)  # espera inicial
    q0 = None
    yaw0 = None
    
    reached = False # Posicion alcanzada

    def quat_to_yaw(qx, qy, qz, qw):
       """Convierte cuaternión a yaw (rad)."""
       siny_cosp = 2.0 * (qw * qz + qx * qy)
       cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
       return math.atan2(siny_cosp, cosy_cosp)


    def wrap_to_pi(angle):
       """Envuelve un ángulo a [-pi, pi]."""
       return (angle + math.pi) % (2.0 * math.pi) - math.pi

    
    def odom_callback(msg):
        nonlocal reached, tol_rad, q0, yaw0
        # Posición
        q = msg.pose.pose.orientation
        yaw = quat_to_yaw(q.x, q.y, q.z, q.w)
        
        if q0 == None:
            q0 = q
            yaw0 = yaw
        
        # Error de orientación
        
        dyaw = yaw - yaw0
        
        e = wrap_to_pi(yaw_ref - dyaw)


        twist = Twist()

        # Si todavía no llegó a la distancia deseada
        if abs(e) > tol_rad:
            w = Kp * e

            # Saturación de velocidad angular
            w_max = 0.3   # rad/s
            if w > w_max:
                w = w_max
            if w < -w_max:
                w = -w_max

            twist.angular.z = w
            twist.linear.x = 0.0
        else:
            # Ya alcanzó la orientación deseada
            twist.angular.z = 0.0
            twist.linear.x = 0.0

            if not reached:
                node.get_logger().info(
                    f'Orientación alcanzada. '
                    f'Yaw ≈ {math.degrees(yaw):.1f} deg'
                )
                reached = True
                pub.publish(twist)
                node.destroy_node()
                rclpy.shutdown()


        pub.publish(twist)
    
    # Suscripción
    sub = node.create_subscription(Odometry,"/odom",
        odom_callback,10)
        
    # Mantener nodo vivo
    rclpy.spin(node)
 

if __name__ == "__main__":
    main()

