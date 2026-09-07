import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    params = os.path.join(
        get_package_share_directory('turtle_py'),
        'config',
        'params.yaml'
    )

    turtlesim = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    publisher = Node(
        package='turtle_py',
        executable='distance_publisher',
        name='distance_publisher',
        parameters=[params],
        output='screen',
    )

    publisher2 = Node(
        package='turtle_py',
        executable='distance_publisher',
        name='distance_publisher',
        namespace='turtle2',
        remappings=[
            ('/turtle1/pose', '/turtle2/pose'),
            ('/turtle_distance', 'turtle_distance'),
        ],
        parameters=[params],
        output='screen',
    )

    watcher = Node(
        package='turtle_py',
        executable='distance_watcher',
        name='distance_watcher',
        parameters=[params],
        output='screen',
    )

    action_server = Node(
        package='turtle_py',
        executable='polygon_action_server',
        name='polygon_action_server',
        parameters=[params],
        output='screen',
    )

    return LaunchDescription([
        turtlesim,
        publisher,
        publisher2,
        watcher,
        action_server
    ])