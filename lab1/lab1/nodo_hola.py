import rclpy   #rclpy: Siempre se debe importar cuando se utilice ROS2 en Python.

#colcon build --symlink-install = prepara tu paquete

#source install/setup.bash = le dice a la terminal que use ese paquete

def main():
  rclpy.init()  # init: Inicializa un nodo ROS2 con el nombre "hola"
  node = rclpy.create_node('hola')
  print("Hola UTEC!")
  node.get_logger().info('Este es un mensaje normal')
  node.get_logger().warn('Este es un mensaje de advertencia')
  node.get_logger().error("Este es un mensaje de error")

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Node stopped by user')
  
  node.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()
