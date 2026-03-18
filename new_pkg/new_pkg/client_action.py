import rclpy
from simple_actions import SimpleActionClient
from action_timer.action import Timer
from builtin_interfaces.msg import Duration


def main():
    rclpy.init()
    node = rclpy.create_node('nombre_cliente')
    client = SimpleActionClient(node, Timer, 'timer')

    goal_msg = Timer.Goal(time_to_wait=Duration(sec=3, nanosec=0))
    result = client(goal_msg)
    print(result)


if __name__ == '__main__':
    main()