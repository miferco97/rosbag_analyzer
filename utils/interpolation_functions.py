import numpy as np
from geometry_msgs.msg import PoseStamped, Point
from utils.ros2_utils import stamp_to_float, float_to_stamp
from rosbags.typesys import Stores, get_typestore

typestore = get_typestore(Stores.LATEST)
        
def check_timestamps(func):
    def wrapper(msg_1, msg_2, t_new: float):
        if not hasattr(msg_1, 'header') or not hasattr(msg_2, 'header'):
            raise ValueError("x and y must be ros2 messages with a header and a time stamp")
        t1 = stamp_to_float(msg_1.header.stamp)
        t2 = stamp_to_float(msg_2.header.stamp)
        if t1 >= t_new:
            return msg_1
        if t2 <= t_new:
            return msg_2
        return func(msg_1, msg_2, t1, t2, t_new)
    return wrapper

def update_header(msg, t_new: float):
    msg.header.stamp = float_to_stamp(t_new)
    return msg

def interpolate_geometry_msgs_Point(msg_1: Point, msg_2: Point, t1:float, t2:float , t_new: float) -> Point:
    """Interpolates the data points (x,y) to the new points x_new"""

    x1 = msg_1.x
    x2 = msg_2.x
    y1 = msg_1.y
    y2 = msg_2.y
    z1 = msg_1.z
    z2 = msg_2.z
    x_new = np.interp(t_new, [t1, t2], [x1, x2])
    y_new = np.interp(t_new, [t1, t2], [y1, y2])
    z_new = np.interp(t_new, [t1, t2], [z1, z2])
    return Point(x=x_new, y=y_new, z=z_new)

@check_timestamps
def interpolate_geometry_msgs_PoseStamped(msg_1: PoseStamped, msg_2: PoseStamped, t1:float, t2:float , t_new: float) -> PoseStamped:
    """Interpolates the data points (x,y) to the new points x_new"""
    point1 = msg_1.pose.position
    point2 = msg_2.pose.position
    
    new_point = interpolate_geometry_msgs_Point(point1, point2, t1, t2, t_new)
    new_pose = PoseStamped()
    new_pose.pose.position = new_point
    new_pose = update_header(new_pose, t_new)
    return new_pose

    
interpolation_catalogue = {
        type(PoseStamped()): interpolate_geometry_msgs_PoseStamped,
        typestore.types["geometry_msgs/msg/PoseStamped"]: interpolate_geometry_msgs_PoseStamped,
        type(Point()): interpolate_geometry_msgs_Point,
        typestore.types["geometry_msgs/msg/Point"]: interpolate_geometry_msgs_Point}



def interpolate(msg_1, msg_2, t_new: float):
    """Interpolates the data points (x,y) to the new points x_new"""
    # check types are equal
    if type(msg_1) != type(msg_2):
        raise ValueError(f'Types {type(msg_1)} and {type(msg_2)} must be equal')
    # check if type is in the interpolation catalogue
    if type(msg_1) not in interpolation_catalogue:

        print(f'Avaliable types: {interpolation_catalogue.keys()}')
        raise ValueError(f'Type {type(msg_1)} is not in the interpolation catalogue')
    
    # get the interpolation 
    interpolation = interpolation_catalogue[type(msg_1)]
    return interpolation(msg_1, msg_2, t_new)

