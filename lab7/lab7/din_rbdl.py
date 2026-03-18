import rbdl
import numpy as np
import pinocchio as pin
np.set_printoptions(suppress=True, precision=3)

"""
para correr en la terminal nueva: python3 ~/lab_ws/src/lab7/lab7/din_rbdl.py

"""

if __name__ == '__main__':

  # Lectura del modelo del robot a partir de URDF (parsing)
  modelo = rbdl.loadModel("/home/cristhian/lab_ws/src/lab7/urdf/ur5_robot.urdf")
  # Grados de libertad
  ndof = modelo.q_size
 
 
  q = np.array([0.5, 0.2, 0.3, 0.8, 0.5, 0.6]) # Configuracion articular
  dq = np.array([0.8, 0.7, 0.8, 0.6, 0.9, 1.0]) # Velocidad articular
  ddq = np.array([0.2, 0.5, 0.4, 0.3, 1.0, 0.5]) # Aceleracion articular

  # Arrays numpy
  zeros = np.zeros(ndof)          # Vector de ceros
  tau   = np.zeros(ndof)          # Para torque
  g     = np.zeros(ndof)          # Para la gravedad
  c     = np.zeros(ndof)          # Para el vector de Coriolis+centrifuga
  M     = np.zeros([ndof, ndof])  # Para la matriz de inercia
  e     = np.eye(6)               # Vector identidad
  
  # Torque dada la configuracion del robot
  rbdl.InverseDynamics(modelo, q, dq, ddq, tau)
  
  # Parte 1: Calcular vector de gravedad, vector de Coriolis/centrifuga,
  # y matriz M usando solamente InverseDynamics
  # --------------------------------------
  # Matriz de gravedad
   # τ = g(q) con dq = 0 y ddq = 0
  rbdl.InverseDynamics(modelo,q,zeros,zeros,tau)
  g= tau.copy() #vector de gravedad g(q)
  
   # τ = c(q, dq) + g(q) con ddq = 0
  rbdl.InverseDynamics(modelo,q,dq,zeros,tau)
  c= tau.copy()-g # c(q, dq) = τ - g(q)
  
  # armar la matriz de inercia M(q)
  # ndof: DOF
  for i in range(ndof):
    #dq = 0
    # τ = M(q)·e_i + g(q)
    rbdl.InverseDynamics(modelo,q,zeros,e[i,:],tau)
    M[i,:] = tau.copy()-g # fila i de M: τ - g(q)
  
  g_rounded = np.round(g, 3)
  c_rounded = np.round(c, 3)
  M_rounded = np.round(M, 3)

  # Imprimir de manera legible
  print("\nVector de gravedad g(q):")
  print(g_rounded)

  print("\nVector de fuerzas centrífugas y de Coriolis c(q, dq):")
  print(c_rounded)

  print("\nMatriz de inercia M(q):")
  print(M_rounded)



#----------------------------
    # === Parte 2: Calcular el vector de torques tau ===
  tau_dyn = M.dot(ddq) + c + g      # tau = M*ddq + c + g

  # Redondear a 3 decimales
  tau_dyn_rounded = np.round(tau_dyn, 3)

  print("\nVector de torques tau = M(q)*ddq + c(q,dq) + g(q):")
  print(tau_dyn_rounded)

  # comparar rbdl con Pinocchio

  rbdl.InverseDynamics(modelo, q, dq, ddq, tau)
  print("tau con rbdl =\n", tau) 


  # Para Pinocchio
  # Lectura del modelo del robot a partir de URDF (parsing)
  model = pin.buildModelFromUrdf("/home/cristhian/lab_ws/src/lab7/urdf/ur5_robot.urdf")
  data = model.createData()

  tau1 = pin.rnea(model, data, q, dq, ddq)
  print("tau con Pinocchio =\n", tau1) 