# funcion que tiene es esperar el asignado
import time
import rclpy
from simple_actions import SimpleActionServer
from action_timer.action import Timer


def do_timer(goal):

    sleep_time = goal.time_to_wait.sec + goal.time_to_wait.nanosec * 1e-9 # tiempo que se va esperar
    time.sleep(sleep_time)

    result = Timer.Result()
    result.updates_send = 0
    result.time_elapsed = goal.time_to_wait
    return result


def main():

    rclpy.init()
    node = rclpy.create_node('nombre_servidor') #nombre del nodo
    SimpleActionServer(node, Timer, 'timer', do_timer)
    rclpy.spin(node)


if __name__ == '__main__':
    main()
