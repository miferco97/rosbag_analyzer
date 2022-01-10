import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

import matplotlib.pyplot as plt

ns = "/drone0"
topics_desired = [ns + "/self_localization/odom" ] 
class BagFileParser():
    def __init__(self, bag_file):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()

        ## create a message type map
        topics_data = self.cursor.execute("SELECT id, name, type FROM topics").fetchall()
        self.topic_type = {name_of:type_of for id_of,name_of,type_of in topics_data if name_of in topics_desired}
        self.topic_id = {name_of:id_of for id_of,name_of,type_of in topics_data if name_of in topics_desired}
        self.topic_msg_message = {name_of:get_message(type_of) for id_of,name_of,type_of in topics_data if name_of in topics_desired}

    def __del__(self):
        self.conn.close()

    # Return [(timestamp0, message0), (timestamp1, message1), ...]
    def get_messages(self, topic_name):

        topic_id = self.topic_id[topic_name]
        # Get from the db
        rows = self.cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = {}".format(topic_id)).fetchall()
        # Deserialise all and timestamp them
        return [ (timestamp,deserialize_message(data, self.topic_msg_message[topic_name])) for timestamp,data in rows]



if __name__ == "__main__":

        bag_file = '../rosbag2_fronton/rosbag2_fronton/rosbag2_2021_12_20-11_18_18_side2side_8ms/rosbag2_2021_12_20-11_18_18_0.db3'

        parser = BagFileParser(bag_file)

        trajectory = parser.get_messages(ns + "/self_localization/odom")
        print(trajectory)
        p_des_1 = [trajectory.points[i].positions[0] for i in range(len(trajectory.points))]
        t_des = [trajectory.points[i].time_from_start.sec + trajectory.points[i].time_from_start.nanosec*1e-9 for i in range(len(trajectory.points))]

        actual = parser.get_messages("/joint_states")

        plt.plot(t_des, p_des_1)

        plt.show()