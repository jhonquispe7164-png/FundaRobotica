import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from action_timer.action import TargetZone


class TargetZoneActionClient(Node):
    def __init__(self):
        # crea el nodo cliente con este nombre
        super().__init__('target_zone_action_client')

        # crea el cliente de acción para 'target_zone'
        self._action_client = ActionClient(self, TargetZone, 'target_zone')

    def send_goal(self, target):
        # crea el mensaje objetivo
        goal_msg = TargetZone.Goal()

        # guarda la zona objetivo que envía el cliente
        goal_msg.target_zone = target

        # espera a que el servidor esté disponible
        self._action_client.wait_for_server()

        # envía el objetivo y define la función que recibirá feedback
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # cuando el servidor responda si aceptó o no, llama a esta función
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        # obtiene la respuesta del servidor
        goal_handle = future.result()

        # si el objetivo no fue aceptado, termina
        if not goal_handle.accepted:
            self.get_logger().info('Objetivo rechazado')
            rclpy.shutdown()
            return

        # si fue aceptado, lo muestra en consola
        self.get_logger().info('Objetivo aceptado')

        # pide el resultado final de la acción
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        # obtiene el feedback enviado por el servidor
        feedback = feedback_msg.feedback

        # muestra la diferencia entre la zona objetivo y la zona actual
        self.get_logger().info(
            f'Diferencia con la zona objetivo: {feedback.difference}'
        )

    def get_result_callback(self, future):
        # obtiene el resultado final
        result = future.result().result

        # muestra si se llegó o no a la zona objetivo
        if result.success:
            self.get_logger().info('Se llegó a la zona objetivo')
        else:
            self.get_logger().info('No se llegó a la zona objetivo')

        # cierra ROS2 al terminar
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    # pide al usuario que escriba la zona objetivo
    target = int(input('Ingrese la zona objetivo (1 al 20): '))

    # crea el nodo cliente
    node = TargetZoneActionClient()

    # envía el objetivo al servidor
    node.send_goal(target)

    # mantiene el nodo activo para recibir feedback y resultado
    rclpy.spin(node)


if __name__ == '__main__':
    main()