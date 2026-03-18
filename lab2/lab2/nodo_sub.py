import rclpy
from std_msgs.msg import Int32


def main():
  rclpy.init()

  node = rclpy.create_node('suscriptor')

  def callback(msg):
        node.get_logger().info(f'Received: {msg.data}')

  subscription = node.create_subscription(Int32, 'counter', callback, 10)
  
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Subscriber stopped by user')

  node.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()
