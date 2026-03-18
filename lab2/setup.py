import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='alex@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'publisher = lab2.nodo_pub:main',
        	'subscriber = lab2.nodo_sub:main',
        	'nodeJoints = lab2.node_joints:main',
            'nodo_joint_tras = lab2.nodo_joint_tras:main',
            'nodo_joint_tras2 = lab2.nodo_joint_tras2:main',
        ],
    },
)
