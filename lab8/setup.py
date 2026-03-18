import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab8'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
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
            'dibujar_triangulo = lab8.dibujar_triangulo:main',
            'odom= lab8.odom:main',
            'ctrl_distancia = lab8.ctrl_distancia:main',
            'ctrl_orientacion3 = lab8.ctrl_orientacion3:main',
            'dibujar_letra3 = lab8.dibujar_letra3:main', 
            'ctrl_orientacion = lab8.ctrl_orientacion:main',
        ],
    },
)