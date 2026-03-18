from setuptools import find_packages, setup

package_name = 'lab1'

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
    maintainer='alex',
    maintainer_email='alex@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'nodo_hola = lab1.nodo_hola:main',
        	'nodo_pub = lab1.nodo_pub:main',
        	'nodo_sub = lab1.nodo_sub:main',
        	
        	'new_pub_I = lab1.new_pub_I:main',
        	'new_pubF = lab1.new_pubF:main',
        	'new_subI = lab1.new_subI:main',
        ],
    },
)
