import pinocchio as pin
import numpy as np

def main():

  # Lectura del modelo del robot a partir de URDF (parsing)
  model = pin.buildModelFromUrdf("/home/cristhian/lab_ws/src/lab7/urdf/ur5_robot.urdf")
  data = model.createData()

  # Evitar usar e-0x
  np.set_printoptions(suppress=True, precision=3)
  
  q = np.array([0.2, 0.1, 1.5, 0.8, 0.2, 0.3])   # Configuracion articular
  dq = np.array([0.3, 0.3, 0.4, 0.3, 0.4, 0.5])  # Velocidad articular
  ddq = np.array([0.3, 0.3, 0.5, 0.1, 0.2, 0.1]) # Aceleracion articular
  
  # Arrays auxiliares
  zeros = np.zeros(model.nq)                     # Vector de ceros
  tau   = np.zeros(model.nq)                     # Para torque
  g     = np.zeros(model.nq)                     # Para la gravedad
  c     = np.zeros(model.nq)                     # Para Coriolis + centrífuga
  M     = np.zeros((model.nq, model.nq))         # Para la matriz de inercia
  
  # Solucionando la dinamica
  # Este cálculo directo con RNEA devuelve el torque total tau para q, dq y ddq.
  dyn_solver = pin.rnea(model, data, q, dq, ddq)
  
  # Parte 1: Calcular vector de gravedad, vector de Coriolis/centrifuga,
  # y matriz M usando Pinocchio

  # g(q): efecto únicamente de la gravedad sobre cada articulación.
  pin.computeGeneralizedGravity(model, data, q)
  g = data.g
  print("g(q) =\n", g)
  
  # Matriz de Coriolis y vector c(q,dq)
  pin.computeCoriolisMatrix(model, data, q, dq)
  C = data.C
  c = C @ dq
  
  print("c(q, qdot) =\n", c)

  # M(q): matriz de inercia articular.
  M = pin.crba(model, data, q)
  print("M(q) =\n", M)

  # Parte 2: Calcular vector tau usando Pinocchio
  # Tau se obtiene a partir del modelo dinámico:
  # tau = M(q)ddq + c(q,dq) + g(q)
  print("--------------------------------------\n")
  tau_recon = M @ ddq + c + g
  print("tau (M*ddq + c + g) =\n", tau_recon)
  
  # Cálculo directo con RNEA para comparar
  tau = pin.rnea(model, data, q, dq, ddq)
  print("tau =\n", tau)


if __name__ == '__main__':
  main()