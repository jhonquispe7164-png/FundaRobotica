#!/usr/bin/env python3
import rclpy
import threading
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from markers import *
from lab5functions import *
from sensor_msgs.msg import JointState

# Grafica
def graficar_error(ee):
  # crear nombre único para no sobreescribir archivos
  nombre = "error_ikine_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"

  # crear figura
  plt.figure()
  plt.plot(np.abs(ee), 'b')
  plt.plot(np.abs(ee), 'b.')
  plt.title("Evolución del error")
  plt.xlabel("Número de iteraciones")
  plt.ylabel("Norma del error")
  plt.grid()

  # guardar gráfica
  plt.savefig(nombre, dpi=300, bbox_inches='tight')
  plt.close()

  print(f"Gráfica del error guardada en: {nombre}")


def main():
  rclpy.init()
  node = rclpy.create_node('ForwardKinematics')
  pub = node.create_publisher(JointState, 'joint_states', 10)
  
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()
  
  #bmarker = BallMarker(node, color['GREEN'])
  marker = FrameMarker(node)
 
  # Joint names
  jnames = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint','wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
  
  # Joint Configuration inicial
  q = np.array([0.0, -np.pi/4, 0.0, 0.0, 0.0, 0.0])

  # Lock para acceso seguro a q
  q_lock = threading.Lock()

  def actualizar_pose():
    T = fkine_ur5(q)
    print("\nMatriz T actual:")
    print(np.round(T, 3))
    x0 = TF2xyzquat(T)
    marker.setPose(x0)

# mostrar pose inicial
  actualizar_pose()

  def leer_posicion_cartesiana():
    nonlocal q
    print("\nIngresa la posición deseada del efector final en metros.")
    print("Formato: x y z")
    print("Ejemplo: 0.30 0.20 0.40")
    print("Escribe 'salir' para terminar.\n")

    while rclpy.ok():
      try:
        entrada = input("xdes[m] > ").strip()

        if entrada.lower() in ['salir', 'exit', 'quit']:
          rclpy.shutdown()
          break

        valores = [float(v) for v in entrada.replace(',', ' ').split()]

        if len(valores) != 3:
          print("Debes ingresar exactamente 3 valores: x y z")
          continue

        xdes = np.array(valores)

        with q_lock:
          q_inicial = q.copy()

        # calcular cinemática inversa
        q_sol, ee = ikine(xdes, q_inicial)    #Metodo newton 

        # graficar y guardar el error
        graficar_error(ee)

        with q_lock:
          q = q_sol

        # calcular pose final alcanzada
        T = fkine_ur5(q)
        x_final = T[0:3, 3]

        print("\nPosición deseada:", np.round(xdes, 4))
        print("Posición alcanzada:", np.round(x_final, 4))
        print("Error inicial:", np.round(ee[0], 6))
        print("Error final:", np.round(ee[-1], 6))
        print("q solución [rad]:", np.round(q, 4))
        print("q solución [deg]:", np.round(np.rad2deg(q), 2))

        x0 = TF2xyzquat(T)
        marker.setPose(x0)

      except Exception as e:
        print("Entrada inválida:", e)

  # hilo para leer la posición desde teclado
  input_thread = threading.Thread(target=leer_posicion_cartesiana, daemon=True)
  input_thread.start()

  # mensaje JointState
  jstate = JointState()
  jstate.header.stamp = node.get_clock().now().to_msg()
  jstate.name = jnames

  # frecuencia del loop
  rate = node.create_rate(20)

  # loop principal
  while rclpy.ok():
    with q_lock:
      q_actual = q.copy()

    jstate.header.stamp = node.get_clock().now().to_msg()
    jstate.position = q_actual.tolist()

    pub.publish(jstate)
    marker.publish()
    rate.sleep()

  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()