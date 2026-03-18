"""
La lógica será esta:

 * recibe la zona objetivo
 * cada segundo genera un número aleatorio entre 1 y 20
 * calcula la diferencia
 * manda feedback
 * si coincide, termina con éxito
 * si llega a 10 intentos sin coincidir, termina con fracaso
"""

import time      # para esperar 1 segundo en cada intento
import random    # para generar un número aleatorio entre 1 y 20

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from action_timer.action import TargetZone


class TargetZoneActionServer(Node):
    def __init__(self):
        # crea el nodo servidor con este nombre
        super().__init__('target_zone_action_server')

        # crea el servidor de acción
        # usa la acción TargetZone
        # el nombre de la acción será 'target_zone'
        # cuando llegue un objetivo se ejecutará execute_callback
        self._action_server = ActionServer(
            self,
            TargetZone,
            'target_zone',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        # muestra en consola que se recibió un objetivo
        self.get_logger().info('Objetivo recibido')

        # obtiene la zona objetivo enviada por el cliente
        target = goal_handle.request.target_zone

        # crea el mensaje de feedback
        feedback_msg = TargetZone.Feedback()

        # crea el mensaje de resultado final
        result = TargetZone.Result()

        # verifica que el objetivo esté dentro del rango permitido
        if target < 1 or target > 20:
            self.get_logger().info('La zona objetivo debe estar entre 1 y 20')
            result.success = False
            goal_handle.abort()
            return result

        # realiza como máximo 10 intentos
        for i in range(10):
            time.sleep(1)  # espera 1 segundo antes de cada intento

            # genera una zona aleatoria entre 1 y 20
            current_zone = random.randint(1, 20)

            # calcula la diferencia entre la zona objetivo y la zona actual
            difference = abs(target - current_zone)

            # coloca esa diferencia en el feedback
            feedback_msg.difference = difference

            # envía el feedback al cliente
            goal_handle.publish_feedback(feedback_msg)

            # muestra en consola el intento, la zona generada y la diferencia
            self.get_logger().info(
                f'Intento {i+1}: zona actual = {current_zone}, diferencia = {difference}'
            )

            # si la zona actual coincide con la objetivo, termina con éxito
            if current_zone == target:
                goal_handle.succeed()
                result.success = True
                return result

        # si después de 10 intentos no coincide, termina con fracaso
        goal_handle.abort()
        result.success = False
        return result


def main(args=None):
    # inicializa ROS2
    rclpy.init(args=args)

    # crea el nodo servidor
    node = TargetZoneActionServer()

    # mantiene el nodo activo esperando objetivos
    rclpy.spin(node)

    # cierra ROS2 al finalizar
    rclpy.shutdown()


if __name__ == '__main__':
    main()