import launch
from launch.substitutions import Command, LaunchConfiguration
import launch_ros
import launch_ros.descriptions
import os

def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(package='snow_white_description').find('snow_white_description')
    default_model_path = os.path.join(pkg_share, 'src/description/snow_white_description.urdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz/urdf_config.rviz')
    joint_state_publisher_gui_node = launch_ros.actions.Node(
         package='joint_state_publisher_gui',
         executable='joint_state_publisher_gui',
         name='joint_state_publisher_gui',
         condition=launch.conditions.IfCondition(LaunchConfiguration('gui'))
        )
    
    world_path=os.path.join(pkg_share, 'world/my_world.sdf')

    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
       )
    
    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
         executable='joint_state_publisher',
         name='joint_state_publisher',
          arguments=[default_model_path],
        )

    joint_state_publisher_gui_node = launch_ros.actions.Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=launch.conditions.IfCondition(LaunchConfiguration('gui'))
         )
    
    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        )

    spawn_entity = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'snow_white', '-topic', 'robot_description'],
        output='screen'
        )
    
    robot_localization_node = launch_ros.actions.Node(
       package='robot_localization',
       executable='ekf_node',
       name='ekf_filter_node',
       output='screen',
       parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
        )

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='gui', default_value='true',
                                            description='Flag to enable joint_state_publisher_gui'),
        launch.actions.DeclareLaunchArgument(name='model', default_value=default_model_path,
                                            description='Absolute path to robot urdf file'),
        launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'),
        launch.actions.ExecuteProcess(cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_path], output='screen'),
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='false',
                                            description='Flag to enable use_sim_time'),

        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        spawn_entity,
        robot_localization_node,
        rviz_node

    ])