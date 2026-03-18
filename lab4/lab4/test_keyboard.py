import rclpy

from std_msgs.msg import String

def main():
  rclpy.init()

  node = rclpy.create_node('suscriptor')

  def callback(msg):
        node.get_logger().info(f'Received: {msg.data}')

  subscription = node.create_subscription(String, 'keys', callback, 10)

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Subscriber stopped by user')

  node.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()

# este de abajo solo se muestra cuando le llega un valor no muestra 0 es decir lo filtra
""""
import rclpy
from std_msgs.msg import String

def main():
  rclpy.init()

  node = rclpy.create_node('suscriptor')

  def callback(msg):
    if msg.data != "0":
      node.get_logger().info(f'Received: {msg.data}')

  subscription = node.create_subscription(String, 'keys', callback, 10)

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Subscriber stopped by user')

  node.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()

"""