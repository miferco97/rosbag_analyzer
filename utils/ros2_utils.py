from builtin_interfaces.msg import Time
from geometry_msgs.msg import Pose, PoseStamped, Point
from rosbags.typesys import Stores, get_typestore
typestore = get_typestore(Stores.LATEST)

def stamp_to_float(stamp: Time) -> float:
    return stamp.sec + stamp.nanosec * 1e-9

def float_to_stamp(t):
    sec = int(t)
    nsec = int((t - sec) * 1e9)
    return Time(sec=sec, nanosec=nsec)

def extract_3d_vector(msg):
    if type(msg) == Pose:
        return [msg.position.x, msg.position.y, msg.position.z]
    if type(msg) == PoseStamped or typestore.types["geometry_msgs/msg/PoseStamped"] == type(msg):
        return [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
    if type(msg) == Point:
        return [msg.x, msg.y, msg.z]
    raise ValueError(f'Type {type(msg)} not supported in extract_3d_vector')

