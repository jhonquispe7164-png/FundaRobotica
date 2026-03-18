#!/usr/bin/env python3
import rclpy #siempre se debe de importar cuando se utilice ROS2 en python 
import threading
from std_msgs.msg import Int32

# rqt_graph: ver los grafos de los topicos y nodos 

"""
La propiedad de este y otros mensajes del paquete “std_msgs”: 

https://docs.ros2.org/foxy/api/std_msgs/index-msg.html
"""

#nodo publicador 
#El siguiente código crea un nodo el cual publica una contador que se incrementa #cada medio segundo. La cuenta se publica en el tópico “/counter”, el cual tiene # # el tipo de #mensaje “Int32”.

def main():
    rclpy.init()
    node = rclpy.create_node('publicador') #nodo publicador 
    publisher = node.create_publisher(Int32, 'counter', 10)
    thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
    thread.start()
    msg = Int32()
    count = 0
    rate = node.create_rate(2)
    while rclpy.ok():
        msg.data = count
        publisher.publish(msg)
        node.get_logger().info(f'Publishing: {msg.data}') #el topico 
        count += 1
        rate.sleep()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

