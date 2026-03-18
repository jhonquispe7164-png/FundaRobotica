#!/usr/bin/env python3
import rclpy
import threading
import numpy as np
import kinpy as kp

from scipy.spatial.transform import Rotation as R
from sensor_msgs.msg import JointState

from lab6.markers import FrameMarker, BallMarker, color
""" Se desarrolló el nodo ik_kinpy, el cual calcula la cinemática inversa del manipulador usando 
la librería KinPy a partir de una posición y orientación deseada del efector final. La solución 
articular obtenida se publica mediante joint_states, permitiendo visualizar en RViz la configuración
correspondiente del robot. ros2 run lab6 ik_kinpy para vizualizar en rviz correr el launch de lab4,
ya que se esta trabajando con el robot ur5 el mismo del lab6 

$ ros2 launch lab4 view_ur_without_sliders.launch.py ur_type:=ur5 
y lazar el nodo ik_kinpy


    desired_frame_marker = FrameMarker(node)                  # orientación deseada
    desired_point_marker = BallMarker(node, color['RED'])    # punto deseado
    reached_point_marker = BallMarker(node, color['GREEN'])  # punto alcanzado
"""

def quat_xyzw_to_wxyz(q_xyzw):
    """
    Convierte cuaternión de formato [x, y, z, w] a [w, x, y, z]
    """
    return np.array([q_xyzw[3], q_xyzw[0], q_xyzw[1], q_xyzw[2]], dtype=float)


def quat_wxyz_to_xyzw(q_wxyz):
    """
    Convierte cuaternión de formato [w, x, y, z] a [x, y, z, w]
    """
    return np.array([q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]], dtype=float)


def kinpy_transform_to_xyzquat(T):
    """
    Convierte kp.Transform a:
    [x, y, z, qx, qy, qz, qw]
    """
    pos = np.array(T.pos, dtype=float)
    quat_xyzw = quat_wxyz_to_xyzw(np.array(T.rot, dtype=float))
    return np.hstack((pos, quat_xyzw))


def main():
    rclpy.init()
    node = rclpy.create_node('ik_kinpy')

    pub = node.create_publisher(JointState, 'joint_states', 10)

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    # Marcadores
    desired_frame_marker = FrameMarker(node)                  # orientación deseada
    desired_point_marker = BallMarker(node, color['RED'])    # punto deseado
    reached_point_marker = BallMarker(node, color['GREEN'])  # punto alcanzado

    # Nombres articulares
    jnames = [
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

    # ==================================================
    # POSE DESEADA
    # ==================================================
    target_pos = np.array([0.5, -0.5, 0.5], dtype=float)

    # orientación deseada en roll-pitch-yaw [rad]
    desired_rpy = np.array([0.2, 0.2, 0.8], dtype=float)

    rot_obj = R.from_euler('xyz', desired_rpy)
    quat_xyzw = rot_obj.as_quat()
    quat_wxyz = quat_xyzw_to_wxyz(quat_xyzw)

    target_transform = kp.Transform(
        rot=quat_wxyz,
        pos=target_pos
    )

    # Semilla inicial
    initial_guess = np.array([0.0, -1.0, 1.0, 0.0, 0.0, 0.0], dtype=float)

    # ==================================================
    # IK
    # ==================================================
    solution = chain.inverse_kinematics(target_transform, initial_guess)

    if isinstance(solution, dict):
        q = np.array([solution[name] for name in jnames], dtype=float)
    else:
        q = np.array(solution, dtype=float)

    # ==================================================
    # FK de verificación
    # ==================================================
    fk_result = chain.forward_kinematics(q)
    reached_pose = kinpy_transform_to_xyzquat(fk_result)
    reached_pos = reached_pose[:3]

    # Pose deseada en formato marker [x,y,z,qx,qy,qz,qw]
    desired_pose = np.hstack((target_pos, quat_xyzw))

    # Errores
    pos_error = target_pos - reached_pos
    pos_error_norm = np.linalg.norm(pos_error)

    # Mostrar resultados
    print("\n================ RESULTADOS IK ================\n")

    print("Posición deseada [x, y, z]:")
    print(np.round(target_pos, 4))

    print("\nOrientación deseada [roll, pitch, yaw] en rad:")
    print(np.round(desired_rpy, 4))

    print("\nOrientación deseada [roll, pitch, yaw] en deg:")
    print(np.round(np.rad2deg(desired_rpy), 2))

    print("\nSolución articular q [rad]:")
    print(np.round(q, 4))

    print("\nSolución articular q [deg]:")
    print(np.round(np.rad2deg(q), 2))

    print("\nPose alcanzada por FK [x, y, z, qx, qy, qz, qw]:")
    print(np.round(reached_pose, 4))

    print("\nError de posición [x, y, z]:")
    print(np.round(pos_error, 6))

    print("\nNorma del error de posición:")
    print(np.round(pos_error_norm, 6))

    print("\n===============================================\n")

    # Configurar marcadores
    desired_frame_marker.setPose(desired_pose)  # muestra orientación deseada
    desired_point_marker.xyz(target_pos)        # punto deseado
    reached_point_marker.xyz(reached_pos)       # punto alcanzado

    # Mensaje JointState
    jstate = JointState()
    jstate.name = jnames

    rate = node.create_rate(20)

    while rclpy.ok():
        jstate.header.stamp = node.get_clock().now().to_msg()
        jstate.position = q.tolist()

        pub.publish(jstate)

        desired_frame_marker.publish()
        desired_point_marker.publish()
        reached_point_marker.publish()

        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()