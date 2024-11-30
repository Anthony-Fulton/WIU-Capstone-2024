import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml

def generate_launch_description():                                                          # Defining the function for launch generation

    snow_white_launch = IncludeLaunchDescription(                                           # Assign a name to the launch
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("snow_white_description"),             # Assign a path to the package
                         "launch/display2.launch.py")                                       # Assign a path to the launch file
        ),
        launch_arguments= {                                                                 # Using simulation time breaks things, so we use a launch argument to set it to false.
            'use_sim_time': 'false',
        }.items()
    )



    slam_toolbox_launch = IncludeLaunchDescription(                                           
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("slam_toolbox"),              
                         "launch/online_async_launch.py")                                        
        ),
        launch_arguments= {                                                                 
            'use_sim_time': 'true',
        }.items()
    )

    navigation2_launch = IncludeLaunchDescription(                                           
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("nav2_bringup"),             
                         "launch/navigation_launch.py")                                        
        ),
        launch_arguments= {                                                                 
            'use_sim_time': 'true',
        }.items()
    )

    return LaunchDescription([
        snow_white_launch,
        slam_toolbox_launch,
        navigation2_launch,
    ])