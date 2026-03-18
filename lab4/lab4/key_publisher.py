#!/usr/bin/env python3
import sys, select, tty, termios
import rclpy
import threading
from std_msgs.msg import String


def main():
  rclpy.init()

  node = rclpy.create_node('keyboard_driver')
  key_pub = node.create_publisher(String, 'keys', 10)
  
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()
  
  msg = String()

  old_attr = termios.tcgetattr(sys.stdin)
  tty.setcbreak(sys.stdin.fileno())
  print("Publishing keystrokes. Press Ctrl-C to exit...")
  
  rate = node.create_rate(10)
  try:
    while rclpy.ok():
      if select.select([sys.stdin], [], [], 0)[0] == [sys.stdin]:
        msg.data = sys.stdin.read(1)
      else:
        msg.data = "0" 
      key_pub.publish(msg) 
      rate.sleep()
    
  except KeyboardInterrupt:
    node.get_logger().info('Publisher stopped by user')
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_attr)
    node.destroy_node()
    rclpy.shutdown()
 

if __name__ == '__main__':
  main()
