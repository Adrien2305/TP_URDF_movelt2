import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Packages
    desc_pkg  = get_package_share_directory('robot_arm_description')
    moveit_pkg = get_package_share_directory('robot_arm_moveit_config')

    # URDF via xacro
    xacro_file = os.path.join(desc_pkg, 'urdf', 'robot_arm.urdf.xacro')
    robot_description = {'robot_description': Command(['xacro ', xacro_file])}

    # SRDF
    srdf_file = os.path.join(moveit_pkg, 'config', 'robot_arm.srdf')
    with open(srdf_file, 'r') as f:
        robot_description_semantic = {'robot_description_semantic': f.read()}

    # Kinematics
    kinematics_yaml = os.path.join(moveit_pkg, 'config', 'kinematics.yaml')

    # Joint limits
    joint_limits_yaml = os.path.join(moveit_pkg, 'config', 'joint_limits.yaml')

    # OMPL planning
    ompl_planning_yaml = os.path.join(moveit_pkg, 'config', 'ompl_planning.yaml')

    # ---------------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------------

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            {'robot_description_kinematics': kinematics_yaml},
            {'robot_description_planning':   joint_limits_yaml},
            ompl_planning_yaml,
            {'use_sim_time': False},
        ],
    )

    rviz_config = os.path.join(moveit_pkg, 'config', 'moveit.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[
            robot_description,
            robot_description_semantic,
            {'robot_description_kinematics': kinematics_yaml},
        ],
    )

    # Joint state publisher (simulation – pas de vrai hardware)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        move_group_node,
        rviz_node,
    ])
