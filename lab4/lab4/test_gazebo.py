#!/usr/bin/env python3
import rclpy
import threading
import numpy as np

from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

from markers import *
from lab4functions import *


def main():

  rclpy.init()
  node = rclpy.create_node('test_gazebo')

  # Hilo para spin del nodo
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()

  # Marker del efector final
  marker = FrameMarker(node)

  # Nombres articulares del UR5
  jnames = [
      'shoulder_pan_joint',
      'shoulder_lift_joint',
      'elbow_joint',
      'wrist_1_joint',
      'wrist_2_joint',
      'wrist_3_joint'
  ]

  # Configuración inicial
  q = np.array([0.0, -np.pi/4, 0.0, 0.0, 0.0, 0.0])

  # Lock para acceso seguro a q
  q_lock = threading.Lock()

  # Caso A:
  # nombre RELATIVO de la action
  # correr luego con:
  # ros2 run lab4 test_gazebo __ns:=joint_trajectory_controller
  action_client = ActionClient(
      node,
      FollowJointTrajectory,
      'follow_joint_trajectory'
  )

  node.get_logger().info('Esperando servidor de acción...')
  action_client.wait_for_server()
  node.get_logger().info('Servidor de acción disponible.')

  def actualizar_pose():
    T = fkine_ur5(q)
    print("\nMatriz T actual:")
    print(np.round(T, 3))
    x0 = TF2xyzquat(T)
    marker.setPose(x0)

  def resultado_callback(future):
    try:
      result = future.result().result
      node.get_logger().info('Movimiento finalizado.')
      node.get_logger().info(str(result))
    except Exception as e:
      node.get_logger().error(f'Error recibiendo resultado: {e}')

  def respuesta_goal_callback(future):
    try:
      goal_handle = future.result()

      if not goal_handle.accepted:
        node.get_logger().warn('Goal rechazado.')
        return

      node.get_logger().info('Goal aceptado.')
      result_future = goal_handle.get_result_async()
      result_future.add_done_callback(resultado_callback)

    except Exception as e:
      node.get_logger().error(f'Error enviando goal: {e}')

  def enviar_trayectoria(q_cmd):
    goal_msg = FollowJointTrajectory.Goal()

    goal_msg.trajectory.joint_names = jnames

    point = JointTrajectoryPoint()
    point.positions = q_cmd.tolist()
    point.time_from_start = Duration(sec=3)

    goal_msg.trajectory.points.append(point)

    node.get_logger().info(f'Enviando trayectoria: {np.round(q_cmd, 3)}')
    future = action_client.send_goal_async(goal_msg)
    future.add_done_callback(respuesta_goal_callback)

  # Calcular pose inicial
  actualizar_pose()

  # Enviar pose inicial al robot en Gazebo
  with q_lock:
    enviar_trayectoria(q.copy())

  def leer_articulaciones():
    nonlocal q

    print("\nIngresa 6 articulaciones en GRADOS separadas por espacio.")
    print("Ejemplo: 0 -45 30 0 90 0")
    print("Escribe 'salir' para terminar.\n")

    while rclpy.ok():
      try:
        entrada = input("q[deg] > ").strip()

        if entrada.lower() in ['salir', 'exit', 'quit']:
          rclpy.shutdown()
          break

        valores = [float(v) for v in entrada.replace(',', ' ').split()]

        if len(valores) != 6:
          print("Debes ingresar exactamente 6 valores.")
          continue

        q_nuevo = np.deg2rad(np.array(valores))

        with q_lock:
          q = q_nuevo
          T = fkine_ur5(q)
          print("\nq [rad] =", np.round(q, 3))
          print("Matriz T actual:")
          print(np.round(T, 3))
          x0 = TF2xyzquat(T)
          marker.setPose(x0)

          # Enviar nueva trayectoria al robot
          enviar_trayectoria(q.copy())

      except Exception as e:
        print("Entrada inválida:", e)

  # Hilo para leer articulaciones desde teclado
  input_thread = threading.Thread(target=leer_articulaciones, daemon=True)
  input_thread.start()

  # Loop para publicar marker
  rate = node.create_rate(20)

  while rclpy.ok():
    marker.publish()
    rate.sleep()

  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()