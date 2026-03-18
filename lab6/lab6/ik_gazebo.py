#!/usr/bin/env python3
import rclpy
import numpy as np
import kinpy as kp

from scipy.spatial.transform import Rotation as R
from simple_actions import SimpleActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

"""
Se desarrolló el nodo ik_gazebo, el cual combina la resolución de la cinemática inversa mediante la 
librería KinPy con el envío de trayectorias articulares al robot simulado en Gazebo. A partir de una posición
y orientación deseada del efector final, se obtiene una configuración articular objetivo y esta se envía 
al controlador joint_trajectory_controller usando la acción FollowJointTrajectory, permitiendo observar 
el movimiento del manipulador en simulación.

En el laboratorio anterior se implementó la cinemática inversa mediante un modelo propio. 
En este laboratorio se utiliza la librería KinPy para resolver la cinemática inversa de forma automática, 
a partir de una pose deseada del efector final. 

$ ros2 launch ur_simulation_gz ur_sim_control.launch.py ur_type:='ur5'
y luego correr el nodo ik_gazebo
"""


def quat_xyzw_to_wxyz(q_xyzw):
    """
    Convierte cuaternión [x, y, z, w] a [w, x, y, z]
    """
    return np.array([q_xyzw[3], q_xyzw[0], q_xyzw[1], q_xyzw[2]], dtype=float)


def wrap_to_pi(q):
    """
    Lleva cada ángulo al rango [-pi, pi]
    """
    return (q + np.pi) % (2.0 * np.pi) - np.pi


def main():
    rclpy.init()
    node = rclpy.create_node('ik_gazebo')

    # Cliente de acción para el controlador de trayectoria en Gazebo
    action_client = SimpleActionClient(
        node,
        FollowJointTrajectory,
        '/joint_trajectory_controller/follow_joint_trajectory'
    )

    # Nombres articulares esperados por el controlador
    joint_names = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'elbow_joint',
        'wrist_1_joint',
        'wrist_2_joint',
        'wrist_3_joint'
    ]

    # Cargar URDF
    urdf_path = "/home/cristhian/lab_ws/src/lab6/urdf/ur5_robot.urdf"
    with open(urdf_path, 'r') as f:
        urdf_text = f.read()

    chain = kp.build_serial_chain_from_urdf(
        urdf_text,
        root_link_name="base_link",
        end_link_name="ee_link"
    )

    # Mostrar orden de joints de kinpy
    kinpy_joint_names = chain.get_joint_parameter_names()
    print("\nJoint names de kinpy:")
    print(kinpy_joint_names)

    print("\nJoint names enviados al controlador:")
    print(joint_names)

    # =========================
    # Pose deseada
    # =========================
    target_pos = np.array([0.5, -0.2, 0.7], dtype=float)
    desired_rpy = np.array([0.2, 0.0, 0.1], dtype=float)   # [roll, pitch, yaw]

    # Euler -> quaternion [x, y, z, w]
    r = R.from_euler('xyz', desired_rpy)
    quat_xyzw = r.as_quat()

    # kinpy usa [w, x, y, z]
    quat_wxyz = quat_xyzw_to_wxyz(quat_xyzw)

    # Transformación objetivo
    target_transform = kp.Transform(
        rot=quat_wxyz,
        pos=target_pos
    )

    # Semilla inicial
    initial_guess = np.array([0.0, -1.0, 1.0, 0.0, 0.0, 0.0], dtype=float)

    # =========================
    # Resolver IK
    # =========================
    solution = chain.inverse_kinematics(target_transform, initial_guess)

    if isinstance(solution, dict):
        q = np.array([solution[name] for name in joint_names], dtype=float)
    else:
        q = np.array(solution, dtype=float)

    # Guardar también la solución cruda
    q_raw = q.copy()

    # Normalizar ángulos para evitar vueltas raras en Gazebo
    q = wrap_to_pi(q)

    # =========================
    # Verificación con FK
    # =========================
    fk_result = chain.forward_kinematics(q)
    reached_pos = np.array(fk_result.pos, dtype=float)

    pos_error = target_pos - reached_pos
    pos_error_norm = np.linalg.norm(pos_error)

    print("\n================ RESULTADOS IK GAZEBO ================\n")

    print("Posición deseada [x, y, z]:")
    print(np.round(target_pos, 4))

    print("\nOrientación deseada [roll, pitch, yaw] en rad:")
    print(np.round(desired_rpy, 4))

    print("\nOrientación deseada [roll, pitch, yaw] en deg:")
    print(np.round(np.rad2deg(desired_rpy), 2))

    print("\nSolución articular q cruda [rad]:")
    print(np.round(q_raw, 4))

    print("\nSolución articular q cruda [deg]:")
    print(np.round(np.rad2deg(q_raw), 2))

    print("\nSolución articular q normalizada [rad]:")
    print(np.round(q, 4))

    print("\nSolución articular q normalizada [deg]:")
    print(np.round(np.rad2deg(q), 2))

    print("\nPosición alcanzada por FK [x, y, z]:")
    print(np.round(reached_pos, 4))

    print("\nError de posición [x, y, z]:")
    print(np.round(pos_error, 6))

    print("\nNorma del error de posición:")
    print(np.round(pos_error_norm, 6))

    print("\n======================================================\n")

    # =========================
    # Enviar trayectoria a Gazebo
    # =========================
    goal = FollowJointTrajectory.Goal()
    traj = JointTrajectory()
    traj.joint_names = joint_names

    # Punto 1: postura inicial conocida
    point1 = JointTrajectoryPoint()
    point1.positions = [0.0, -np.pi/2, 0.0, 0.0, 0.0, 0.0]
    point1.time_from_start.sec = 2
    point1.time_from_start.nanosec = 0

    # Punto 2: solución IK
    point2 = JointTrajectoryPoint()
    point2.positions = q.tolist()
    point2.time_from_start.sec = 6
    point2.time_from_start.nanosec = 0

    traj.points.append(point1)
    traj.points.append(point2)
    goal.trajectory = traj

    print("Enviando trayectoria al controlador de Gazebo...\n")
    result = action_client.send_goal(goal)

    print("Resultado de la acción:")
    print(result)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()