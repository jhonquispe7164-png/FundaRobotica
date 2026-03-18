import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from action_timer.action import Timer
from builtin_interfaces.msg import Duration

# Actividad 2.2: El servidor manda feedback al cliente durante la ejecución, y al final manda el resultado.


class TimerActionClient(Node):
    def __init__(self):
        # crea el nodo cliente con este nombre
        super().__init__('timer_action_client')

        # crea el cliente de acción que se conectará a la acción 'timer'
        self._action_client = ActionClient(self, Timer, 'timer')

    def send_goal(self):
        # crea el mensaje de objetivo que se enviará al servidor
        goal_msg = Timer.Goal()

        # indica que el temporizador debe esperar 5 segundos
        goal_msg.time_to_wait = Duration(sec=5, nanosec=0)

        # espera hasta que el servidor de acción esté disponible
        self._action_client.wait_for_server()

        # envía el objetivo de forma asíncrona
        # además, indica qué función recibirá el feedback
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # cuando el servidor responda si aceptó o no el objetivo,
        # se ejecutará esta función
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        # obtiene la respuesta del servidor
        goal_handle = future.result()

        # si el servidor no acepta el objetivo, muestra mensaje y cierra ROS2
        if not goal_handle.accepted:
            self.get_logger().info('Objetivo rechazado')
            rclpy.shutdown()
            return

        # si el objetivo fue aceptado, lo muestra en consola
        self.get_logger().info('Objetivo aceptado')

        # pide el resultado final de la acción
        self._get_result_future = goal_handle.get_result_async()

        # cuando el resultado esté listo, llama a esta función
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        # extrae el feedback recibido del servidor
        feedback = feedback_msg.feedback

        # muestra en consola el tiempo restante
        self.get_logger().info(
            f'Feedback -> tiempo restante: {feedback.time_remaining.sec} s'
        )

    def get_result_callback(self, future):
        # obtiene el resultado final enviado por el servidor
        result = future.result().result

        # muestra el tiempo total transcurrido
        self.get_logger().info(
            f'Resultado final -> tiempo transcurrido: {result.time_elapsed.sec} s'
        )

        # muestra cuántos feedback fueron enviados
        self.get_logger().info(
            f'Total de feedback enviados: {result.updates_send}'
        )

        # cierra ROS2 cuando ya terminó todo
        rclpy.shutdown()


def main(args=None):
    # inicializa ROS2
    rclpy.init(args=args)

    # crea el nodo cliente
    node = TimerActionClient()

    # envía el objetivo al servidor
    node.send_goal()

    # mantiene el nodo activo para recibir feedback y resultado
    rclpy.spin(node)


if __name__ == '__main__':
    main()