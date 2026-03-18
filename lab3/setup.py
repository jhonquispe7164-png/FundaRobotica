import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='jlopezm@utec.edu.pe',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'send_joints = lab3.send_joints:main',
            'send_cmd_vel = lab3.send_cmd_vel:main',
            'pub_sensor = lab3.pub_sensor:main',
            'new_node_joints = lab3.new_node_joints:main',
            'new_send_joints = lab3.new_send_joints:main',
            
        ],
    },
)
