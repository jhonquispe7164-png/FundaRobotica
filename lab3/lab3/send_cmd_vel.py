#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

"""
ros2 launch lab3 mobile_diffdrive.launch
ros2 run ros_gz_sim create -name mobile_bot -topic robot_description -z 0.1
ros2 run controller_manager spawner joint_state_broadcaster
ros2 run controller_manager spawner diff_drive_controller
ros2 run lab3 send_cmd_vel
"""

class SendCmdVel(Node):
    def __init__(self):
        super().__init__('send_cmd_vel')
        self.pub = self.create_publisher(
            Twist,
            '/diff_drive_controller/cmd_vel_unstamped',
            10
        )
        self.timer = self.create_timer(0.1, self.publish_cmd)
        self.t0 = time.time()

    def publish_cmd(self):
        t = time.time() - self.t0
        msg = Twist()

        if t < 3.0:
            msg.linear.x = 0.2
            msg.angular.z = 0.0
        elif t < 6.0:
            msg.linear.x = 0.0
            msg.angular.z = 0.8
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.pub.publish(msg)
        self.get_logger().info(
            f'vx={msg.linear.x:.2f}, wz={msg.angular.z:.2f}'
        )


def main():
    rclpy.init()
    node = SendCmdVel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()