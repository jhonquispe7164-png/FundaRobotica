#!/usr/bin/env python3
import rclpy
import time
import numpy as np
import kinpy as kp

from scipy.spatial.transform import Rotation as R
from simple_actions import SimpleActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

"""
Lanzar primero:
ros2 launch ur_simulation_gz ur_sim_control.launch.py ur_type:=ur5

Luego:
ros2 run lab6 draw_rectangle_gazebo
"""

def quat_xyzw_to_wxyz(q_xyzw):
    return np.array([q_xyzw[3], q_xyzw[0], q_xyzw[1], q_xyzw[2]], dtype=float)


def interpolar(p0, p1, n):
    puntos = []
    for i in range(n):
        t = i / (n - 1)
        p = (1 - t) * p0 + t * p1
        puntos.append(p)
    return puntos


def nearest_equivalent_angle(q_new, q_ref):
    """
    Para una articulación, elige entre q_new + 2*pi*k la solución
    más cercana a q_ref.
    """
    candidates = [q_new + 2.0 * np.pi * k for k in range(-3, 4)]
    return min(candidates, key=lambda x: abs(x - q_ref))


def make_q_continuous(q_new, q_ref):
    """
    Ajusta cada articulación para que quede en la rama más cercana
    a la configuración anterior q_ref.
    """
    q_adj = np.zeros_like(q_new)
    for i in range(len(q_new)):
        q_adj[i] = nearest_equivalent_angle(q_new[i], q_ref[i])
    return q_adj


def main():
    rclpy.init()
    node = rclpy.create_node('draw_rectangle_gazebo')

    action_client = SimpleActionClient(
        node,
        FollowJointTrajectory,
        '/joint_trajectory_controller/follow_joint_trajectory'
    )

    joint_names = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'elbow_joint',
        'wrist_1_joint',
        'wrist_2_joint',
        'wrist_3_joint'
    ]

    # =========================
    # Cargar URDF y cadena de KinPy
    # =========================
    urdf_path = "/home/cristhian/lab_ws/src/lab6/urdf/ur5_robot.urdf"
    with open(urdf_path, 'r') as f:
        urdf_text = f.read()

    chain = kp.build_serial_chain_from_urdf(
        urdf_text,
        root_link_name="base_link",
        end_link_name="ee_link"
    )

    print("\nJoint names de kinpy:")
    print(chain.get_joint_parameter_names())

    # =========================
    # Rectángulo de prueba
    # =========================
    # Primero probamos uno pequeño y bien ubicado
    ancho = 0.30   # 12 cm
    alto  = 0.21   # 16 cm

    # Plano paralelo a XZ -> y constante
    x_centro = 0.30
    y_const  = 0.55
    z_base   = 0.50  # > 10 cm

    if z_base < 0.10:
        raise ValueError("La base del rectángulo está por debajo de 10 cm.")

    p1 = np.array([x_centro - ancho/2, y_const, z_base], dtype=float)         # inferior izquierdo
    p2 = np.array([x_centro - ancho/2, y_const, z_base + alto], dtype=float)  # superior izquierdo
    p3 = np.array([x_centro + ancho/2, y_const, z_base + alto], dtype=float)  # superior derecho
    p4 = np.array([x_centro + ancho/2, y_const, z_base], dtype=float)         # inferior derecho

    # =========================
    # Interpolación
    # =========================
    n_lado_vertical = 12
    n_lado_horizontal = 10

    seg1 = interpolar(p1, p2, n_lado_vertical)
    seg2 = interpolar(p2, p3, n_lado_horizontal)[1:]
    seg3 = interpolar(p3, p4, n_lado_vertical)[1:]
    seg4 = interpolar(p4, p1, n_lado_horizontal)[1:]

    # Para probar el trazo completo
    path_xyz = seg1 + seg2 + seg3 + seg4

    for i, p in enumerate(path_xyz):
        if p[2] < 0.10:
            raise ValueError(f"El punto {i} viola z >= 0.10: {p}")

    # =========================
    # Orientación fija del efector final
    # =========================
    # Ajuste más razonable para que la herramienta "mire" de lado
    desired_rpy = np.array([np.pi/2, 0.0, np.pi/2], dtype=float)

    rot_obj = R.from_euler('xyz', desired_rpy)
    quat_xyzw = rot_obj.as_quat()
    quat_wxyz = quat_xyzw_to_wxyz(quat_xyzw)

    # =========================
    # IK punto a punto
    # =========================
    q_seed = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)
    q_list = []

    print("\nResolviendo IK para cada punto...\n")

    for i, xdes in enumerate(path_xyz):
        target_transform = kp.Transform(
            rot=quat_wxyz,
            pos=xdes
        )

        solution = chain.inverse_kinematics(target_transform, q_seed)

        if isinstance(solution, dict):
            q_raw = np.array([solution[name] for name in joint_names], dtype=float)
        else:
            q_raw = np.array(solution, dtype=float)

        # ESTA ES LA CLAVE:
        # no envolver a [-pi, pi] a ciegas; hay que mantener continuidad
        q_sol = make_q_continuous(q_raw, q_seed)

        fk_result = chain.forward_kinematics(q_sol)
        reached_pos = np.array(fk_result.pos, dtype=float)

        pos_error = xdes - reached_pos
        err_norm = np.linalg.norm(pos_error)

        print(f"Punto {i+1}/{len(path_xyz)}")
        print("xdes =", np.round(xdes, 4))
        print("xalc =", np.round(reached_pos, 4))
        print("error =", np.round(pos_error, 6))
        print("norma error =", np.round(err_norm, 6))
        print("q =", np.round(q_sol, 4))

        if i > 0:
            dq = q_sol - q_list[-1]
            print("dq =", np.round(dq, 4))
        print()

        q_list.append(q_sol.copy())
        q_seed = q_sol.copy()

    # =========================
    # Crear trayectoria articular
    # =========================
    goal = FollowJointTrajectory.Goal()
    traj = JointTrajectory()
    traj.joint_names = joint_names

    # Ir primero al primer punto real del dibujo
    point0 = JointTrajectoryPoint()
    point0.positions = q_list[0].tolist()
    point0.velocities = [0.0] * 6
    point0.time_from_start.sec = 4
    point0.time_from_start.nanosec = 0
    traj.points.append(point0)

    dt = 0.8
    t0 = 4.0

    for i, q in enumerate(q_list[1:]):
        point = JointTrajectoryPoint()
        point.positions = q.tolist()
        point.velocities = [0.0] * 6

        tiempo = t0 + (i + 1) * dt
        sec = int(tiempo)
        nanosec = int((tiempo - sec) * 1e9)

        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        traj.points.append(point)

    goal.trajectory = traj

    print("Enviando trayectoria para dibujar el rectángulo en Gazebo...\n")
    result = action_client.send_goal(goal)

    print("Resultado de la acción:")
    print(result)

    tiempo_total = t0 + (len(q_list) - 1) * dt + 2.0
    print(f"Esperando {tiempo_total:.1f} s para que termine la trayectoria...")
    time.sleep(tiempo_total)

    print("Trayectoria terminada.")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()