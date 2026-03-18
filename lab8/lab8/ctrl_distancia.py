#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("ctrl_distancia")
    pub = node.create_publisher(Twist, "/cmd_vel", 10)

    # Parámetros
    d_ref = 1.0 #m
    Kp = 0.7
    tol = 0.005       # tolerancia (m)
    time.sleep(1.0)  # espera inicial
    
    reached = False # Posicion alcanzada
    x0 = None
    y0 = None
    
    def odom_callback(msg):
        nonlocal x0, y0, reached, tol
        # Posición
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        
        # Guardar la posición inicial en la primera lectura
        if x0 is None or y0 is None:
            x0 = x
            y0 = y
            node.get_logger().info(
                f'Posición inicial: x0={x0:.3f}, y0={y0:.3f}'
            )
            return
            
        # Distancia recorrida desde la posición inicial
        dx = x - x0
        dy = y - y0
        d = math.sqrt(dx*dx + dy*dy)
        
        # 
        # Error de distancia
        e = d_ref - d

        twist = Twist()

        # Si todavía no llegó a la distancia deseada
        if e > tol:   # tolerancia de 1 cm
            v = Kp * e

            # Saturación de la velocidad para que no sea muy grande
            v_max = 0.26
            if v > v_max:
                v = v_max
            if v < 0.0:
                v = 0.0

            twist.linear.x = v
            twist.angular.z = 0.0
        else:
            # Ya llegó: detenerse
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            if not reached:
                node.get_logger().info(
                    f'Distancia alcanzada. d={d:.3f} m (ref={d_ref:.3f} m)'
                )
                reached = True
                
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


