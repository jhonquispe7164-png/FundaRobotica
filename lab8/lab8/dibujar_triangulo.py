#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DibujarTriangulo(Node):
    def __init__(self):
        super().__init__('dibujar_triangulo')

        # Publicador a /cmd_vel
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer a 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)

        # Parámetros del movimiento
        self.v = 0.2        # m/s velocidad lineal 
        self.t_side = 5.0   # s  ->  v * t_side = 0.2 * 5 = 1 m
        self.w = 0.5        # rad/s 
        self.t_turn = 4.19  # s  ->  w * t_turn = 120° tiempo de giro  

        # Estado de la “máquina de estados”
        self.state = 'forward'   # 'avanza' o 'girando'
        self.edge = 0            # contador cuántos lados ya dibujó el triangulo 
        self.t0 = self.get_clock().now()

    def elapsed(self):
        """Segundos transcurridos desde t0.""" 
        return (self.get_clock().now() - self.t0).nanoseconds / 1e9  # 

    def control_loop(self):
        msg = Twist()

        # Si ya dibujó los 3 lados: parar y no hacer nada más
        if self.edge >= 3:
            # Twist en cero
            self.pub.publish(msg)
            return

        if self.state == 'forward':
            # Avanzar recto durante t_side segundos
            if self.elapsed() < self.t_side:
                msg.linear.x = self.v
            else:
                # Termina el tramo recto, pasar al giro
                msg.linear.x = 0.0
                self.state = 'turn'
                self.t0 = self.get_clock().now()

        elif self.state == 'turn':
            # Girar durante t_turn segundos
            if self.elapsed() < self.t_turn:
                msg.angular.z = self.w
            else:
                # Termina el giro
                msg.angular.z = 0.0
                self.edge += 1
                if self.edge < 3:
                    # Siguiente lado
                    self.state = 'forward'
                    self.t0 = self.get_clock().now()
                else:
                    self.get_logger().info('Triángulo completado')
                    # Luego solo enviará Twists en cero

        # Publicar el comando de velocidad actual
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DibujarTriangulo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
