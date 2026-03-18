#!/usr/bin/env python3
import rclpy #siempre se debe de importar cuando se utilice ROS2 en python 
from std_msgs.msg import Int32 # Tipo de mensaje Int32 (entero de 32 bits)


#Nodo suscriptor 
#Nodo que va recibir el mensaje publicados por el nodo publicador se conecta al 
# topico counter, con el tipo de mensaje "Int32" el code se queda a la espera de recibir un mensje, el mensaje recibido se publica usando la función nombre "callback" 
# el mensaje recibido se define en la varibale "msg" 


# Función callback:
# Se ejecuta AUTOMÁTICAMENTE cada vez que llega un mensaje al tópico 'counter'.

def callback(msg):
    # msg es un objeto de tipo Int32, su dato está en msg.data
    print("Received: " + str(msg.data))

def main():
    rclpy.init()     # Inicializa el sistema de comunicaciones de ROS 2

    # Crea un nodo llamado 'suscriptor'
    node = rclpy.create_node('suscriptor')

    # Crea la suscripción:
    # - Tipo de mensaje: Int32
    # - Tópico: 'counter'
    # - callback: función que procesa el mensaje recibido
    # - 10: tamaño de la cola (buffer de mensajes)
    subscription = node.create_subscription(Int32,'counter',callback,10)

    try:
        # Mantiene el nodo "vivo" escuchando mensajes.
        # Cada vez que llega un mensaje a 'counter' se llama a callback(msg)
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Si paras con Ctrl+C, muestra un mensajito
        node.get_logger().info('Subscriber stopped by user')

    # Limpia recursos al salir
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

