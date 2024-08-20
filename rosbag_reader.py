from pathlib import Path

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore


class RosbagReader():
    """ Class to read rosbags and extract data from them. """
    def __init__(self, rosbag_path: str) -> None:
        self.rosbag_path = Path(rosbag_path)
        if not self.rosbag_path.exists():
            raise FileNotFoundError(f"{self.rosbag_path} not found.")
        # Create a typestore and get the string class.
        self.typestore = get_typestore(Stores.LATEST)

    def read(self, topic_list, namespace=None) -> dict[str, list]:
        local_topic_list = []
        if namespace is not None:
            namespace = namespace if namespace.endswith('/') else namespace + '/'
            namespace = namespace if namespace.startswith('/') else '/' + namespace
            for topic in topic_list:
                if topic.startswith('/'):
                    local_topic_list.append(topic)
                else:
                    local_topic_list.append(namespace + topic)

        data = {}
        print(f"Reading topics: {local_topic_list}")
        
        """ Read the rosbag and return the messages from the topics in the list. returns a dictionary with the topic name as key and the messages as value. """
        with Reader(self.rosbag_path) as reader:
            connections = [x for x in reader.connections if x.topic in local_topic_list]
            if not connections:
                print(f"No connections found for topics: {local_topic_list}")
                return data
            for connection, _ , rawdata in reader.messages(connections=connections):
                msg = self.typestore.deserialize_cdr(rawdata, connection.msgtype)
                if not connection.topic in data:
                    data[connection.topic] = []
                data[connection.topic].append(msg)
        return data

if __name__ == '__main__':
    bagpath ='../rosbag2_2024_07_29-gates_cf_tello/rosbag2_2024_07_29-4_laps'
    bag = RosbagReader(bagpath)
    topics = ['self_localization/pose']
    data = bag.read(topics, namespace='/cf0')
    total_msgs = 0
    for topic, msgs in data.items():
        print(f"Topic: {topic} has {len(msgs)} messages.")
        total_msgs += len(msgs)
    print(f"Total messages read: {total_msgs}")
    
