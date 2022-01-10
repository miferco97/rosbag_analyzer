import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
from typing import Type
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d


namespace = "/drone1/"
wanted_topics = [namespace + "self_localization/pose", "/mocap_node/Robot_1/pose"]


class BagFileParser:
    def __init__(self, bag_file, topics_desired: str):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()

        ## create a message type map
        topics_data = self.cursor.execute(
            "SELECT id, name, type FROM topics"
        ).fetchall()
        self.topic_type = {
            name_of: type_of
            for id_of, name_of, type_of in topics_data
            if name_of in topics_desired
        }
        self.topic_id = {
            name_of: id_of
            for id_of, name_of, type_of in topics_data
            if name_of in topics_desired
        }
        self.topic_msg_message = {
            name_of: get_message(type_of)
            for id_of, name_of, type_of in topics_data
            if name_of in topics_desired
        }

    def __del__(self):
        self.conn.close()

    # Return [(timestamp0, message0), (timestamp1, message1), ...]
    def get_messages(self, topic_name):

        topic_id = self.topic_id[topic_name]
        # Get from the db
        rows = self.cursor.execute(
            "SELECT timestamp, data FROM messages WHERE topic_id = {}".format(topic_id)
        ).fetchall()
        # Deserialise all and timestamp them
        return [
            (timestamp, deserialize_message(data, self.topic_msg_message[topic_name]))
            for timestamp, data in rows
        ]

    def generate_topics_formatted(self):
        print("Loading topics from bag file")
        topics_data = []
        first_time = None
        for name in self.topic_id:
            if not name.endswith("/odom"):
                data = self.get_messages(name)
                new_topic = TopicMsgsBag(name)
                for elem in data:
                    time = elem[0]
                    msg = elem[1]
                    new_topic.addData(time, msg)
                    if first_time is None:
                        first_time = time
                    else:
                        if time < first_time:
                            first_time = time
                topics_data.append(new_topic)
            else:
                new_pose_name = name.replace("/odom", "/pose")
                new_twist_name = name.replace("/odom", "/twist")
                data = self.get_messages(name)
                new_pose_topic = TopicMsgsBag(new_pose_name)
                new_twist_topic = TopicMsgsBag(new_twist_name)
                for elem in data:
                    time = elem[0]
                    msg = elem[1]
                    new_pose_topic.addData(time, msg.pose)
                    new_twist_topic.addData(time, msg.twist)
                    if first_time is None:
                        first_time = time
                    else:
                        if time < first_time:
                            first_time = time
                topics_data.append(new_pose_topic)
                topics_data.append(new_twist_topic)

        print("Done loading topics")
        return topics_data, first_time


def readRosbag(bagfile: str, wanted_topics):

    bag = BagFileParser(bagfile, wanted_topics)
    return bag.generate_topics_formatted()


def calculateOffset(mocap, state_estimator):
    return mocap.getFirstMeasure() - state_estimator.getFirstMeasure()


class TopicMsgsBag:
    def __init__(self, topic_name: str) -> None:
        self.topic_name = topic_name
        self.msgs = []
        self.ros_times = []
        self.incremental_times = []
        self.sync_time = []
        self.sync_msgs = []
        # self.data=[]
        self.initial_time = None

    def getTopicName(self):
        return self.topic_name

    def addData(self, t, msg):
        self.ros_times.append(t)
        self.msgs.append(msg)

    def setInitialTime(self, initial_t):
        self.initial_time = initial_t
        self.incremental_times.clear()
        for t in self.ros_times:
            # print("t: ", t)
            # print("initial_t: ", initial_t)
            time = (t - initial_t) * 1e-9
            print("time", time)

            self.incremental_times.append(time)

    def getData(self, filter_function=None):
        if filter_function is not None:
            return [filter_function(x) for x in self.msgs]

        return self.msgs

    def getTime(self, get_incremental_time=True):
        if get_incremental_time:
            if self.initial_time is not None:
                return self.incremental_times
            else:
                raise AssertionError(
                    "Initial time is not defined for " + self.topic_name + " topic"
                )
        else:
            return self.ros_times

    def calculateTimeIndex(self, t0_delay=0):
        if t0_delay == 0:
            return 0
        elif t0_delay == -1:
            return -1

        index = 0
        while self.incremental_times[index] < t0_delay:
            if index - 1 < len(self.incremental_times):
                index += 1
            else:
                return index
        return max(index - 1, 0)

    def cutFromTimeToTime(self, t_begin=0, t_end=-1):
        t0 = self.calculateTimeIndex(t_begin)
        tend = self.calculateTimeIndex(t_end)
        self.msgs = self.msgs[t0:tend]
        self.incremental_times = np.array(self.incremental_times[t0:tend]) - t_begin

    def syncronizeToTimeSeries(self, objective_time_serie):
        print("syncronizing ", self.topic_name, " data")
        data = self.msgs
        topic_time = self.incremental_times
        syncronized_topic = []
        last_index = 0
        for t_obj in objective_time_serie:
            index = np.max([last_index - 1, 0])
            while topic_time[index] < t_obj:
                index += 1
            t_lower = topic_time[index - 1]
            t_upper = topic_time[index]
            if abs(t_lower - t_obj) < abs(t_upper - t_obj):
                syncronized_topic.append(data[index - 1])
            else:
                syncronized_topic.append(data[index])

        self.sync_msgs = syncronized_topic
        self.sync_time = objective_time_serie

    def getSyncData(self, filter_function=None):
        if filter_function is not None:
            return [filter_function(x) for x in self.sync_msgs]
        return self.sync_msgs

    def getSyncTime(self):
        return self.sync_time


def obtain3DposeVect():
    """
    if ('mocap' in self.topic_name):
        positions_array = np.array([[msg.pose.position.x-MOCAP_OFFSET[0]],[msg.pose.position.y-MOCAP_OFFSET[1]],[msg.pose.position.z-MOCAP_OFFSET[2]]])
    else:
        positions_array = np.array([[msg.pose.position.x],[msg.pose.position.y],[msg.pose.position.z]])
    if self.positions is None:
        self.positions = positions_array
    else:
        self.positions = np.concatenate((self.positions,positions_array),axis=1)

    def plotData(self, figure,color):
        figure.plot(self.positions[0,:],self.positions[1,:],self.positions[2,:],color=color)



    def getFirstMeasure(self):
        return self.positions[:,1]

    """
    pass


def main():
    ROSBAG_FILE = "../rosbag2_fronton/rosbag2_fronton/rosbag2_2021_12_20-11_18_18_side2side_8ms/rosbag2_2021_12_20-11_18_18_0.db3"
    topics, time = readRosbag(
        ROSBAG_FILE,
        wanted_topics=[
            "/drone0/self_localization/odom",
            "/drone0/motion_reference/trajectory",
        ],
    )
    print(topics)
    print(time)


if __name__ == "__main__":
    main()
