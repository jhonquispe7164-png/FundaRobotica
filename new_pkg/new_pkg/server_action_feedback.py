import time  # para manejar la espera de 1 segundo

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from action_timer.action import Timer
from builtin_interfaces.msg import Duration

# Actividad 2.2: El servidor manda feedback al cliente durante la ejecución, y al final manda el resultado.

class TimerActionServer(Node):
    def __init__(self):
        # crea el nodo con este nombre
        super().__init__('timer_action_server')

        # crea el servidor de acción
        # usa la acción Timer
        # el nombre de la acción será 'timer'
        # cuando llegue una meta, se ejecuta execute_callback
        self._action_server = ActionServer(
            self,
            Timer,
            'timer',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        # muestra en consola que el servidor recibió un objetivo
        self.get_logger().info('Objetivo recibido')

        # obtiene los segundos que pidió el cliente
        total_seconds = goal_handle.request.time_to_wait.sec

        # esta variable irá bajando segundo a segundo
        remaining_seconds = total_seconds

        # cuenta cuántas veces se envió feedback
        updates = 0

        # mensaje de feedback que se enviará al cliente
        feedback_msg = Timer.Feedback()

        # mensaje final de resultado
        result = Timer.Result()

        # guarda el instante en el que empieza la acción
        start_time = time.time()

        # este bucle se ejecuta mientras aún queden segundos por esperar
        while remaining_seconds > 0:
            time.sleep(1.0)  # espera 1 segundo
            remaining_seconds -= 1  # reduce en 1 el tiempo restante

            # actualiza el feedback con el tiempo que falta
            feedback_msg.time_remaining = Duration(
                sec=remaining_seconds,
                nanosec=0
            )

            # envía ese feedback al cliente
            goal_handle.publish_feedback(feedback_msg)

            # muestra en consola cuánto tiempo falta
            self.get_logger().info(
                f'Tiempo restante: {remaining_seconds} s'
            )

            # aumenta el contador de feedback enviados
            updates += 1

        # calcula cuánto tiempo pasó realmente
        elapsed = time.time() - start_time

        # separa la parte entera en segundos
        elapsed_sec = int(elapsed)

        # separa la parte decimal en nanosegundos
        elapsed_nanosec = int((elapsed - elapsed_sec) * 1e9)

        # indica que la acción terminó correctamente
        goal_handle.succeed()

        # guarda en el resultado el tiempo total transcurrido
        result.time_elapsed = Duration(
            sec=elapsed_sec,
            nanosec=elapsed_nanosec
        )

        # guarda cuántas actualizaciones de feedback se enviaron
        result.updates_send = updates

        # devuelve el resultado final al cliente
        return result


def main(args=None):
    # inicializa ROS2
    rclpy.init(args=args)

    # crea el nodo servidor
    node = TimerActionServer()

    # mantiene el nodo activo esperando metas
    rclpy.spin(node)

    # cierra ROS2 cuando termina
    rclpy.shutdown()


if __name__ == '__main__':
    main()