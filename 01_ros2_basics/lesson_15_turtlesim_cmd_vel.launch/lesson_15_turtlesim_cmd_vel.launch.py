"""turtlesim과 직진 Publisher를 함께 실행합니다."""

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # turtlesim turtlesim_node
    
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen'
    )
    # cmd_vel publisher

    cmd_vel_publisher_node = Node(
        package='turtle_robot',
        executable='lesson_05_cmd_vel_publisher',
        name='cmd_vel_publisher',
        output='screen'
    )
    return LaunchDescription([
        turtlesim_node,
        cmd_vel_publisher_node])    
