import launch
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import launch_ros
import launch_ros.descriptions
import os

def generate_launch_description():      
                                                                                                # Defining the function for launch generation
    pkg_share = launch_ros.substitutions.FindPackageShare(package='snow_white_description').find('snow_white_description')      # This finds our package
    default_model_path = os.path.join(pkg_share, 'src/description/snow_white_description_v2.urdf')                              # This finds the URDF file
    default_model_path2 = os.path.join(pkg_share, 'src/description/snow_white_description_v2.sdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz/urdf_config.rviz')                                                 # This finds our RViz config
    world_path=os.path.join(pkg_share, 'world/my_world.world')                                                                    # This finds the world used in Gazebo
    ros_gz_sim = launch_ros.substitutions.FindPackageShare(package='ros_gz_sim').find('ros_gz_sim')

    # joint_state_publisher_gui_node = launch_ros.actions.Node(                                                                   # Name our node inside of our code, then launch it
    #      package='joint_state_publisher_gui',                                                                                   # What package does the node come from?
    #      executable='joint_state_publisher_gui',                                                                                # What executable in that package does it need to use?
    #      name='joint_state_publisher_gui',                                                                                      # Name the node itself for when it is launched.
    #      condition=launch.conditions.IfCondition(LaunchConfiguration('gui'))                                                    # Launch configs.
    #     )

    # set_env_vars_resources = AppendEnvironmentVariable(
    #     'GZ_SIM_RESOURCE_PATH',
    #     os.path.join(get_package_share_directory('turtlebot3_gazebo'),
    #                  'models'))

    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'robot_description': Command(['xacro ', LaunchConfiguration('model')])},
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ]
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
    
    robot_localization_node = launch_ros.actions.Node(
       package='robot_localization',
       executable='ekf_node',
       name='ekf_filter_node',
       output='screen',
       parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
        )
   
    # Jury rigging this so that it launches Gazebo in a way I actually understand.
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v4 ', world_path], 'on_exit_shutdown': 'true'}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v4 '}.items()
    )

    create = launch_ros.actions.Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'snow_white', 
                   '-file', default_model_path2],
        output='screen'
        )
    
    bridge_params = os.path.join(get_package_share_directory('snow_white_description'), 'params', 'snow_white_description_bridge.yaml')

    start_gazebo_ros_bridge_cmd = launch_ros.actions.Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args', '-p', 
            f'config_file:={bridge_params}',
        ],
        output='screen'
        )

    start_gazebo_ros_image_bridge_cmd = launch_ros.actions.Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
        output='screen',
    )

    static_transform_publisher = launch_ros.actions.Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['map', 'odom'],
        output='screen',
    )

    return launch.LaunchDescription([                                                                                           # This is just a bunch of launch arguments.
        launch.actions.DeclareLaunchArgument(name='gui', default_value='false',
                                            description='Flag to enable joint_state_publisher_gui'),
        launch.actions.DeclareLaunchArgument(name='model', default_value=default_model_path,
                                            description='Absolute path to robot urdf file'),
        launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'),
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='true',
                                            description='Flag to enable use_sim_time'),

        joint_state_publisher_node,
        # joint_state_publisher_gui_node,
        gzserver_cmd,
        gzclient_cmd,
        # set_env_vars_resources,
        robot_state_publisher_node,
        create,
        robot_localization_node,
        rviz_node,
        start_gazebo_ros_bridge_cmd,
        start_gazebo_ros_image_bridge_cmd,
        static_transform_publisher

    ])