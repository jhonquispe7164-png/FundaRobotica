import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lab5'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ],
    install_requires=['setuptools'],
    py_modules=['markers','lab5functions'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='jlopezm@utec.edu.pe',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'test_ikine = lab5.test_ikine:main',
            'command_gazebo = lab5.command_gazebo:main',
            'draw_a_gazebo = lab5.draw_a_gazebo:main',

        
        ],
    },
)
