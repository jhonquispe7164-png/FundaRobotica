#!/usr/bin/env python3
import rclpy
import numpy as np
from simple_actions import SimpleActionClient
from control_msgs.action import FollowJointTrajectory #la accion ya definida 
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint #servidor Ese controlador recibe la trayectoria y mueve el UR5.




"""
command_gazebo.py = cliente

joint_trajectory_controller = servidor

Tu nodo dice:

“robot, quiero que vayas a esta configuración articular en cierto tiempo”

y el servidor responde:

“ok, recibí la trayectoria y la ejecuto”
"""

def main():
    
  # Iniciar un nodo
  rclpy.init()
  node = rclpy.create_node('command_gazebo')
  
  
  # Declara la acción del tipo cliente
  action_client = SimpleActionClient(
      node,
      FollowJointTrajectory,
      '/joint_trajectory_controller/follow_joint_trajectory'
  )
    
  # Declara las variables del brazo robotico
  # Lista de nombre
  joint_names  = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint','wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
  # Lista de valores de la configuracion del robot
  Q0 = [0.0, -np.pi/2, 0.0, 0.0, 0.0, 0.0] # a la configuración que se desea que se mueva el robot en gazebo
 
  # Definir el tipo de mensaje a utilizar
  goal = FollowJointTrajectory.Goal()    
  traj = JointTrajectory()
  point = JointTrajectoryPoint()
  
  # Definir los nombres de las articulaciones de traj.joint_names
  traj.joint_names = joint_names

  # Definir la posicion inicial de point
  point.positions = Q0

  # Definir el tiempo para llegar al point
  point.time_from_start.sec = 4
  point.time_from_start.nanosec = 0
  
  # Agregar el punto a la trayectoria
  traj.points.append(point)
  goal.trajectory = traj
  
  # Enviar el objetivo y esperar por el resultado
  result = action_client.send_goal(goal)
  
  # Imprimir el resultado
  print(result)

  node.destroy_node()
  rclpy.shutdown()
  
  
if __name__ == '__main__':
  main()
  
