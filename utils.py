import re
from typing import Type
from genmsg import msgs
import rospy
import rosbag
import sys,pdb
from rospy import topics
import std_msgs
import geometry_msgs
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d


namespace = "/drone1/"
wanted_topics = [ namespace+"self_localization/pose", "/mocap_node/Robot_1/pose"]
    

def readRosbag (bagfile:str, wanted_topics:str):
    bag = rosbag.Bag(bagfile)
    pubs = {}
    rospy.loginfo('Start read')
    last = None
    data = []
    topics_data = []
    first_time=None

    for topic, msg, t in tqdm(bag.read_messages()):
        if topic not in wanted_topics:
            continue
        if topic not in [x.getTopicName() for x in topics_data]:
            topics_data.append(TopicMsgsBag(topic))
        if t!=last:        
            if first_time is None:
                first_time = t
            data.append( (t, []) )
            last = t
        data[-1][1].append( (topic, msg) )
    rospy.loginfo('Done read')

    for _t,_data in data:
        topic, msg = _data[0]
        for topic_obj in topics_data:
            if topic_obj.topic_name == topic:
                topic_obj.addData(_t,msg)
    
    bag.close()

    return topics_data, first_time

def calculateOffset(mocap, state_estimator):
    return mocap.getFirstMeasure() - state_estimator.getFirstMeasure()

class TopicMsgsBag():
    def __init__(self,
                 topic_name:str) -> None:
        self.topic_name = topic_name
        self.msgs = []
        self.ros_times= []
        self.incremental_times = []
        self.sync_time=[]
        self.sync_msgs=[]
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
            self.incremental_times.append((t-initial_t).to_sec())

    def getData(self, filter_function = None ):
        if filter_function is not None:
            return [filter_function(x) for x in self.msgs]

        return self.msgs

    def getTime(self, get_incremental_time = True):
        if get_incremental_time :
            if self.initial_time is not None:
                return self.incremental_times
            else:
                raise AssertionError("Initial time is not defined for " + self.topic_name +" topic" )
        else:
            return self.ros_times

    def calculateTimeIndex(self,t0_delay = 0):
        if t0_delay == 0:
            return 0
        elif t0_delay == -1:
            return -1

        index = 0
        while self.incremental_times[index]<t0_delay: 
            if index-1 < len(self.incremental_times):
                index += 1
            else:
                return index
        return max(index-1,0)

    def cutFromTimeToTime(self,t_begin=0,t_end=-1):
        t0 = self.calculateTimeIndex(t_begin)
        tend = self.calculateTimeIndex(t_end)
        self.msgs = self.msgs[t0:tend]
        self.incremental_times = np.array(self.incremental_times[t0:tend]) - t_begin

    
    def syncronizeToTimeSeries(self,objective_time_serie):
        print("syncronizing ", self.topic_name, " data")
        data = self.msgs
        topic_time = self.incremental_times
        syncronized_topic = []
        last_index = 0
        for t_obj in objective_time_serie:
            index = np.max([last_index-1,0])
            while topic_time[index] < t_obj:
                index += 1
            t_lower = topic_time[index-1]
            t_upper = topic_time[index]
            if abs(t_lower-t_obj) < abs(t_upper-t_obj):
                syncronized_topic.append(data[index-1])
            else:
                syncronized_topic.append(data[index])

        self.sync_msgs = syncronized_topic
        self.sync_time = objective_time_serie

    def getSyncData(self, filter_function = None):
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