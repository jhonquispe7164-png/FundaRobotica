#!/usr/bin/env python3
import rclpy
import threading
import numpy as np
from sensor_msgs.msg import JointState
from markers import *
from functions import *
import pinocchio as pin                # Librería de dinámica del robot UR5

# control PD + gravedad

def main():
  rclpy.init()  # Inicializa ROS2
  node = rclpy.create_node('control_pdg')
  pub = node.create_publisher(JointState, 'joint_states', 10)
  
  thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
  thread.start()
  
  #bmarker_actual  = BallMarker(color['RED'])
  #bmarker_deseado = BallMarker(color['GREEN'])
  
  # Archivos donde se almacenara los datos
  fqact = open("/home/cristhian/lab_ws/src/lab7/lab7/qactual.txt", "w")
  fqdes = open("/home/cristhian/lab_ws/src/lab7/lab7/qdeseado.txt", "w")
  fxact = open("/home/cristhian/lab_ws/src/lab7/lab7/xactual.txt", "w")
  fxdes = open("/home/cristhian/lab_ws/src/lab7/lab7/xdeseado.txt", "w")
  
  # Nombres de las articulaciones
  jnames = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
          'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
  # Objeto (mensaje) de tipo JointState
  jstate = JointState()
  # Valores del mensaje
  jstate.header.stamp = node.get_clock().now().to_msg()
  jstate.name = jnames
  
  # =============================================================
  # Configuracion articular inicial (en radianes)
  q = np.array([0.0, 1.0, 1.7, -2.2, -1.6, 0.0])
  # Velocidad inicial
  dq = np.array([0., 0., 0., 0., 0., 0.])
  # Configuracion articular deseada
  qdes = np.array([1.0, -1.0, 1.0, 1.3, -1.5, 1.0])
  # =============================================================
  
  # Posicion resultante de la configuracion articular deseada
  xdes = ur5_fkine(qdes)[0:3,3] # cinematica directa 
  # Copiar la configuracion articular en el mensaje a ser publicado
  jstate.position = q.tolist() # publica la configuración incial
  pub.publish(jstate)
  
  # ======================================================
  # Definir metodos de Pinocchio para el UR5
  # Para Pinocchio
  # Lectura del modelo del robot a partir de URDF (parsing)
  model = pin.buildModelFromUrdf("/home/cristhian/lab_ws/src/lab7/urdf/ur5_robot.urdf")
  data = model.createData() # Memoria interna que usa Pinocchio

  ndof = model.nv             # Número de grados de libertad del UR5
  dqdes = np.zeros(ndof)      # Velocidad deseada = 0 (objetivo estático)

  #tau1 = pin.rnea(model, data, q, dq, ddq)
  #=========================================================

  # Frecuencia del envio (en Hz)
  freq = 50
  dt = 1.0/freq
  rate = node.create_rate(freq)
  
  # Simulador dinamico del robot
  #robot = Robot(q, dq, dt)

  # ----- Inicializar el simulador dinámico -----
  robot = Robot(q, dq, ndof, dt)

  zeros = np.zeros(model.nq)   # Vector cero para calcular gravedad

  # =====================================================
  #            MATRICES DE GANANCIA DEL CONTROL PD+G

  # Se definen las ganancias del controlador
  #Kp = ?
  # Matriz proporcional Kp (diagonal 6x6)
  kp_vec = np.array([2, 0.75, 0.75, 2.5, 3, 3])
  Kp = np.diag(kp_vec)
  
  #Kd = ?
  # Matriz derivativa Kd (diagonal 6x6)
  #subamortiguado
  #kd_vec = np.array([2.2, 2.0, 2.2, 1.5, 0.35, 0.15])
  #Kd = np.diag(kd_vec) # ||e|| = 0.01974404121221091
  
  # Críticamente amortiguado
  #kd_vec = np.array([5.5, 5.4, 6.0, 4.0, 1.0, 0.5])
  #Kd = np.diag(kd_vec)  # ||e|| = 0.019955592194500292
  
  # Sobreamortiguado
  kd_vec = np.array([9.0, 8.5, 9.5, 6.5, 1.8, 1.0])
  Kd = np.diag(kd_vec)  #||e|| = 0.01999190368928358


  # Bucle de ejecucion continua
  t = 0.0
  tol = 0.02
  while rclpy.ok():
  
    # Leer valores del simulador
    q  = robot.read_joint_positions()
    dq = robot.read_joint_velocities()
    # Posicion actual del efector final
    x = ur5_fkine(q)[0:3,3]
    # Tiempo actual (necesario como indicador para ROS)
    jstate.header.stamp = node.get_clock().now().to_msg()

    # Almacenamiento de datos
    fxact.write(str(t)+' '+str(x[0])+' '+str(x[1])+' '+str(x[2])+'\n')
    fxdes.write(str(t)+' '+str(xdes[0])+' '+str(xdes[1])+' '+str(xdes[2])+'\n')
    fqact.write(str(t)+' '+str(q[0])+' '+str(q[1])+' '+ str(q[2])+' '+ str(q[3])+' '+str(q[4])+' '+str(q[5])+'\n ')
    fqdes.write(str(t)+' '+str(qdes[0])+' '+str(qdes[1])+' '+ str(qdes[2])+' '+ str(qdes[3])+' '+str(qdes[4])+' '+str(qdes[5])+'\n ')

    # ----------------------------
    # Control dinamico (COMPLETAR)
    # ----------------------------
    # 1) Obtener el vector de gravedad g(q)
    g = pin.computeGeneralizedGravity(model, data, q)


    # 2) Calcular errores de posición y velocidad
    e  = qdes - q        # Error proporcional
    de = dqdes - dq      # Error derivativo
    # ---- CRITERIO DE PARADA (error “óptimo”) ----
    if np.linalg.norm(e) < tol:
      print("Criterio de parada alcanzado. ||e|| =", np.linalg.norm(e))
      break
    tmax = 100
    if t >= tmax:
      print("Tiempo máximo alcanzado. ||e|| =", np.linalg.norm(e))
      break

    u = u = Kp @ e + Kd @ de + g   # Reemplazar por la ley de control
  
    
    # Simulacion del robot
    robot.send_command(u) # Enviar torque al simulador dinámico

    # Publicar la posición actual al tópico joint_states
    jstate.position = q.tolist()
    pub.publish(jstate)
    #bmarker_deseado.xyz(xdes)
    #bmarker_actual.xyz(x)
    t = t+dt   # Avanzar tiempo
    # Esperar hasta la siguiente  iteracion
    rate.sleep()

  fqact.close()
  fqdes.close()
  fxact.close()
  fxdes.close()
  
  node.destroy_node()
  rclpy.shutdown()
  thread.join(timeout=1.0)


if __name__ == '__main__':
  main()
