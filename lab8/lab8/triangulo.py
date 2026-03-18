#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
import time
import math


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("dibujar_triangulo")
    pub = node.create_publisher(Twist, "/cmd_vel", 10)

    # Parámetros
    vel_linear = 0.2 # m/s
    vel_angular = 0.6 # rad/s
    lado = 1.0 #m
    angulo_giro = math.radians(120) 

    time.sleep(1.0) # pausa 1 segundos

    def mover_recto(distancia):
        twist = Twist()
        twist.linear.x = vel_linear
        duracion = distancia / vel_linear

        t0 = time.time() # tiempo actual en s
        while time.time() - t0 < duracion:
            pub.publish(twist)
            time.sleep(0.1)

        pub.publish(Twist())  # parar


    def girar(angulo):
        twist = Twist()
        twist.angular.z = vel_angular
        duracion = abs(angulo) / vel_angular

        t0 = time.time() # tiempo actual en s
        while time.time() - t0 < duracion:
            pub.publish(twist)
            time.sleep(0.1)

        pub.publish(Twist())  # parar


    def dibujar_triangulo():
        for i in range(3):
            node.get_logger().info(f"Lado {i+1}: moviendo recto...")
            mover_recto(lado)

            node.get_logger().info(f"Giro {i+1}: girando 120°...")
            girar(angulo_giro)

        node.get_logger().info("Triángulo completado.")
        pub.publish(Twist())

    # Ejecutar
    dibujar_triangulo()

    # Mantener nodo vivo
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


