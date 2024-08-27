import numpy as np
from geometry_msgs.msg import PoseStamped, Point
from utils.interpolation_functions import interpolate
from utils.ros2_utils import stamp_to_float, float_to_stamp
from utils.timeseries import interpolate_data

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

def test_multiple_interpolation():
    data= {'test_topic': []}
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
    msg_3 = PoseStamped()
    msg_3.pose.position.x = 0.0
    msg_3.pose.position.y = 0.0
    msg_3.pose.position.z = 0.0
    msg_3.header.stamp = float_to_stamp(2.0)
    data['test_topic'].append(msg_1)
    data['test_topic'].append(msg_2)
    data['test_topic'].append(msg_3)

    time_series = np.arange(0.0, 2.0, 0.1)
    interpolated_data = interpolate_data(data['test_topic'], time_series)
    assert len(interpolated_data) == len(time_series)
    for i, msg in enumerate(interpolated_data):
        assert abs(stamp_to_float(msg.header.stamp) - time_series[i]) < 1e-6
    assert interpolated_data[0].pose.position == msg_1.pose.position




    



