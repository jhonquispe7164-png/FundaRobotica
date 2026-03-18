#!/usr/bin/env python3
import rclpy
import threading
import numpy as np
from lab6.markers import *
from lab6functions import *
from sensor_msgs.msg import JointState


"""
Lo que completa esa parte es:

  - calcular la posición actual x
  - calcular el Jacobiano de posición J
  - calcular el error e = xd - x
  - usar k = 0.5
  - aplicar la pseudo-inversa
  - actualizar q

Y para verificar si llega, mira el valor que se imprime en:
"""


def main():
  rclpy.init()
  node = rclpy.create_node('testKinematicControlPosition')
  pub = node.create_publisher(JointState, 'joint_states', 10)
  
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()
  
  # Files for the logs
  fxcurrent = open("/home/cristhian/lab_ws/src/lab6/lab6/xcurrent.txt", "w")                
  fxdesired = open("/home/cristhian/lab_ws/src/lab6/lab6/xdesired.txt", "w")
  fq = open("/home/cristhian/lab_ws/src/lab6/lab6/q.txt", "w")

  # Markers for the current and desired positions
  bmarker_current = BallMarker(node, color['RED'])
  bmarker_desired = BallMarker(node, color['GREEN'])

  # Joint names
  jnames = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
 
  # Desired position
  xd = np.array([-0.45, -0.20, 0.6])
  # Initial configuration
  q0 = np.array([0.0, -1.0, 1.7, -2.2, -1.6, 0.0])

  # Resulting initial position (end effector with respect to the base link)
  T = fkine_ur5(q0)
  x0 = T[0:3,3]

  # El marcador rojo muestra la posición alcanzada
  bmarker_current.xyz(x0)
  
  # El marcador verde muestra la posición deseada
  bmarker_desired.xyz(xd)

  # Object (message) whose type is JointState
  jstate = JointState()
  # Set values to the message
  jstate.header.stamp = node.get_clock().now().to_msg()
  jstate.name = jnames
  # Add the head joint value (with value 0) to the joints
  jstate.position = q0.tolist()

  # Frequency (in Hz) and control period 
  freq = 50
  dt = 1.0/freq
  rate = node.create_rate(20)

  # Initial joint configuration
  q = copy(q0)
  # Main loop
  while rclpy.ok():
    
    # Hora actual (necesario para ROS)
    jstate.header.stamp = node.get_clock().now().to_msg()
    # Ley de control cinemático para la posición (completa aquí)
    # -----------------------------
    T = fkine_ur5(q)
    x = T[0:3,3]

    J = jacobian_position(q)

    e = xd - x
    k = 0.5

    qdot = np.linalg.pinv(J).dot(k*e)

    q = q + qdot*dt

    T = fkine_ur5(q)
    x = T[0:3,3]

    print("Error de posición:", np.linalg.norm(xd - x))
    # -----------------------------

        
    # Log values                                                      
    fxcurrent.write(str(x[0])+' '+str(x[1]) +' '+str(x[2])+'\n')
    fxdesired.write(str(xd[0])+' '+str(xd[1])+' '+str(xd[2])+'\n')
    fq.write(str(q[0])+" "+str(q[1])+" "+str(q[2])+" "+str(q[3])+" "+
             str(q[4])+" "+str(q[5])+"\n")
        
    # Publish the message
    jstate.position = q.tolist()
    pub.publish(jstate)
    bmarker_desired.xyz(xd)
    bmarker_current.xyz(x)
    # Wait for the next iteration
    rate.sleep()

  print('ending motion ...')
  fxcurrent.close()
  fxdesired.close()
  fq.close()

if __name__ == '__main__':
  main()
