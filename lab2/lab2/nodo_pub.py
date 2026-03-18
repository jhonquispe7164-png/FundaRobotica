import rclpy
from std_msgs.msg import Int32
import threading

def main():
  rclpy.init()
  node = rclpy.create_node('publicador')
  publisher = node.create_publisher(Int32, 'counter', 10)
  
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()
  
  msg = Int32()
  
  node.declare_parameter("count", 0)
  count = node.get_parameter("count").get_parameter_value().integer_value

  rate = node.create_rate(2)
  try:
    while rclpy.ok():
      msg.data = count
      publisher.publish(msg)
      node.get_logger().info(f'Publishing: {msg.data}')
      count += 1
      rate.sleep()
  except KeyboardInterrupt:
    node.get_logger().info('Publisher stopped by user')
  
  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()
