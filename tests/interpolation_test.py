import numpy as np
from geometry_msgs.msg import PoseStamped, Point
from utils.interpolation_functions import interpolate
from utils.ros2_utils import stamp_to_float, float_to_stamp

def test_pose_interpolation():
    msg_1 = PoseStamped()
    msg_1.pose.position.x = 0.0
    msg_1.pose.position.y = 0.0
    msg_1.pose.position.z = 0.0
    msg_1.header.stamp = float_to_stamp(0.0)
    msg_2 = PoseStamped()
    msg_2.pose.position.x = 1.0
    msg_2.pose.position.y = 1.0
    msg_2.pose.position.z = 1.0
    msg_2.header.stamp = float_to_stamp(1.0)
    t_new = 0.5
    new_msg = interpolate(msg_1, msg_2, t_new)
    assert stamp_to_float(new_msg.header.stamp) == t_new
    assert new_msg.pose.position.x == 0.5
    assert new_msg.pose.position.y == 0.5
    assert new_msg.pose.position.z == 0.5



