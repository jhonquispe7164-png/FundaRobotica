from setuptools import find_packages, setup

package_name = 'new_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cristhian',
    maintainer_email='cristhian@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'server_action = new_pkg.server_action:main',
        'client_action = new_pkg.client_action:main',
        'client_action_feedback = new_pkg.client_action_feedback :main',
        'server_action_feedback  = new_pkg.server_action_feedback :main',
        'client_action_TargetZone  = new_pkg.client_action_TargetZone :main',
        'server_action_TargetZone = new_pkg.server_action_TargetZone :main',
        ],
    },
)
