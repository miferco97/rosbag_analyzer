#!/usr/bin/python3

from evaluation_functions import compareStateEstimationWithGroundTruth
from typing import Type
import sys, pdb
import matplotlib.pyplot as plt
import numpy as np

from utils_ros2 import *
from evaluation_functions import *

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d


T_BEGIN = 0
T_END = -1
STEP = 0.1

namespace = "/drone0/"
wanted_topics = [
    namespace + "self_localization/odom",
    "/mocap_node/Robot_1/pose",
    namespace + "self_localization/speed",
    namespace + "self_localization/pose",
    namespace + "motion_reference/trajectory",
]

if __name__ == "__main__":
    bagfn = None
    for arg in sys.argv[1:]:
        if ".bag" or ".db3" in arg:
            bagfn = arg
    if bagfn is None:
        print("No Bag specified!")
        exit(1)

    topics_data, initial_time = readRosbag(bagfn, wanted_topics)

    beggining_times = []
    end_times = []
    for topic in topics_data:
        topic.setInitialTime(initial_time)
        topic.cutFromTimeToTime(T_BEGIN, T_END)
        beggining_times.append(topic.getTime()[0])
        end_times.append(topic.getTime()[-1])

    print("beggining_times", beggining_times)

    time_serie = np.arange(np.max(beggining_times), np.min(end_times), step=STEP)
    for topic in topics_data:
        topic.syncronizeToTimeSeries(time_serie)

    # print(len(topics_data))
    gt_vs_st = True
    speed_analysis = True
    traj_following = True

    mocap_data_array = [x for x in topics_data if "mocap" in x.topic_name]
    if mocap_data_array:
        mocap_data = mocap_data_array[0]
    else:
        gt_vs_st = False

    estimator_pose_array = [
        x for x in topics_data if "self_localization/pose" in x.topic_name
    ]

    if estimator_pose_array:
        estimator_pose = estimator_pose_array[0]
    else:
        traj_following = False
        gt_vs_st = False

    estimator_speed_array = [
        x for x in topics_data if "self_localization/speed" in x.topic_name
    ]
    if estimator_speed_array:
        estimator_speed = estimator_speed_array[0]
    else:
        speed_analysis = False

    traj_data_array = [
        x for x in topics_data if "motion_reference/trajectory" in x.topic_name
    ]
    if traj_data_array:
        traj_data = traj_data_array[0]
    else:
        speed_analysis = False
        traj_following = False

    print("BEGINNING ANALYSIS OF DATA \n")
    if gt_vs_st:
        compareStateEstimationWithGroundTruth(estimator_pose, mocap_data)
    if traj_following:
        trajectoryFollowingEvaluation(traj_data, estimator_pose)
    if speed_analysis:
        SpeedAnalysis(traj_data, estimator_speed)

    plt.show()

    exit()
