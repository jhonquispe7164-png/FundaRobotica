#!/usr/bin/env python3
import rclpy
import time
import numpy as np

from simple_actions import SimpleActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from lab5functions import ikine


def interpolar(p0, p1, n):
    puntos = []
    for i in range(n):
        t = i / (n - 1)
        p = (1 - t) * p0 + t * p1
        puntos.append(p)
    return puntos


def main():

    rclpy.init()
    node = rclpy.create_node('draw_a_gazebo')

    # cliente de acción
    action_client = SimpleActionClient(
        node,
        FollowJointTrajectory,
        '/joint_trajectory_controller/follow_joint_trajectory'
    )

    # nombres de articulaciones
    joint_names = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'elbow_joint',
        'wrist_1_joint',
        'wrist_2_joint',
        'wrist_3_joint'
    ]

    # configuración inicial para arrancar IK
    q_seed = np.array([0.0, -np.pi/2, 0.0, 0.0, 0.0, 0.0])

    # -------------------------------
    # Letra A en el plano XZ
    # -------------------------------
    L = 0.12                     # 12 cm
    h = np.sqrt(3) * L / 2.0     # altura del triángulo equilátero
    y_const = 0.35              # plano XZ => y constante
    x_centro = 0.30
    z_base = 0.62

    p_left  = np.array([x_centro - L/2, y_const, z_base])
    p_top   = np.array([x_centro,       y_const, z_base + h])
    p_right = np.array([x_centro + L/2, y_const, z_base])

    # barra del medio
    p_mid_left  = 0.5 * (p_left + p_top)
    p_mid_right = 0.5 * (p_right + p_top)

    # segmentos de la A
    seg1 = interpolar(p_left, p_top, 10)
    seg2 = interpolar(p_top, p_right, 10)[1:]
    seg3 = interpolar(p_right, p_mid_right, 6)[1:]
    seg4 = interpolar(p_mid_right, p_mid_left, 6)[1:]

    path_xyz = seg1 + seg2 + seg3 + seg4

    # -------------------------------
    # IK para cada punto
    # -------------------------------
    q_list = []

    for i, xdes in enumerate(path_xyz):
        q_sol, ee = ikine(xdes, q_seed)
        q_seed = q_sol.copy()
        q_list.append(q_sol.copy())

        print(f"\nPunto {i+1}/{len(path_xyz)}")
        print("xdes =", np.round(xdes, 4))
        print("q =", np.round(q_sol, 4))
        print("error final =", np.round(ee[-1], 6))

    # -------------------------------
    # Crear trayectoria articular
    # -------------------------------
    goal = FollowJointTrajectory.Goal()
    traj = JointTrajectory()
    traj.joint_names = joint_names

    dt = 0.5   # más lento para que sí se vea el dibujo
    t0 = 1.0   # pequeño tiempo inicial

    for i, q in enumerate(q_list):
        point = JointTrajectoryPoint()
        point.positions = q.tolist()

        tiempo = t0 + (i + 1) * dt
        sec = int(tiempo)
        nanosec = int((tiempo - sec) * 1e9)

        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        traj.points.append(point)

    goal.trajectory = traj

    print("\nEnviando trayectoria para dibujar la letra A...")
    action_client.send_goal(goal)

    # esperar a que termine toda la trayectoria
    tiempo_total = t0 + len(q_list) * dt + 2.0
    print(f"Esperando {tiempo_total:.1f} s para que el robot termine el movimiento...")
    time.sleep(tiempo_total)

    print("Trayectoria terminada.")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()