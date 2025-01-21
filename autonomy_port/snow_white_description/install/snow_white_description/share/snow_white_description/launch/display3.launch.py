import launch
from launch.substitutions import Command, LaunchConfiguration
import launch_ros
import launch_ros.descriptions
import os

def generate_launch_description():                                                                                              # Defining the function for launch generation
    pkg_share = launch_ros.substitutions.FindPackageShare(package='snow_white_description').find('snow_white_description')      # This finds our package
    default_model_path = os.path.join(pkg_share, 'src/description/snow_white_description_v2.urdf')                              # This finds the URDF file
    default_rviz_config_path = os.path.join(pkg_share, 'rviz/urdf_config.rviz')                                                 # This finds our RViz config
    world_path=os.path.join(pkg_share, 'world/world_only.model')                                                                    # This finds the world used in Gazebo


    joint_state_publisher_gui_node = launch_ros.actions.Node(                                                                   # Name our node inside of our code, then launch it
         package='joint_state_publisher_gui',                                                                                   # What package does the node come from?
         executable='joint_state_publisher_gui',                                                                                # What executable in that package does it need to use?
         name='joint_state_publisher_gui',                                                                                      # Name the node itself for when it is launched.
         condition=launch.conditions.IfCondition(LaunchConfiguration('gui'))                                                    # Launch configs.
        )

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

    return launch.LaunchDescription([                                                                                           # This is just a bunch of launch arguments.
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