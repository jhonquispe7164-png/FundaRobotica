import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab6'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*'))
    ],
    install_requires=['setuptools'],
    py_modules=['markers','lab6functions'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='jlopezm@utec.edu.pe',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test_diffkine = lab6.test_diffkine:main',
            'test_kinpy = lab6.test_kinpy:main',
            'ik_kinpy = lab6.ik_kinpy:main',
            'ik_gazebo = lab6.ik_gazebo:main',
            'draw_rectangle_gazebo = lab6.draw_rectangle_gazebo:main',
        ],
    },
)
