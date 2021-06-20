from math import dist, sqrt
from operator import gt
from typing import Type

from numpy.core.defchararray import count
import rospy
import rosbag
import sys,pdb
from rospy import topics
import std_msgs
import geometry_msgs
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

from utils import *
from math_functions import *
from plot_functions import *



def getXpose(msg) :
    return msg.pose.position.x
def getYpose(msg) :
    return msg.pose.position.y
def getZpose(msg) :
    return msg.pose.position.z

def getXspeed(msg) :
    return msg.twist.linear.x
def getYspeed(msg) :
    return msg.twist.linear.y
def getZspeed(msg) :
    return msg.twist.linear.z






def compareStateEstimationWithGroundTruth(se_topic, gt_topic):
  

    se_positions = np.array([se_topic.getSyncData(getXpose),se_topic.getSyncData(getYpose),se_topic.getSyncData(getZpose)])
    gt_positions = np.array([gt_topic.getSyncData(getXpose),gt_topic.getSyncData(getYpose),gt_topic.getSyncData(getZpose)])
    
    time = se_topic.getSyncTime()
    
    gt_offset = se_positions[:,1]-gt_positions[:,1]
    
    print("GROUND_TRUTH OFFSET: ", gt_offset)

    gt_positions = gt_positions + np.reshape(gt_offset,[3,1])

    y_labels = ['x (m)','y (m)','z (m)']
    fig1 = plot3Subplots1perAxis(gt_positions,se_positions,time,
                            x_axis_label="time(s)",
                            y_axis_labels=y_labels,
                            title="State estimation vs Groundthruth",
                            line_1_label="ground thuth",
                            line_2_label="estimation")

    plotErrorPerAxis(   gt_positions,se_positions,time,
                        x_axis_label="time(s)",
                        y_axis_label="error(m)",
                        title= "State estimation error",
                        line_labels=["x_error","y_error","z_error"])
    
    plotTotalError(     gt_positions,se_positions,time,
                        x_axis_label="time(s)",
                        y_axis_label="error(m)",
                        title= "State estimation error",
                        line_label=["error"])

    
    
    print("STATE ESTIMATION ERROR")
    

    axesbyaxesRMSE(se_positions,gt_positions)
    error, dists =Calculate3Derror(se_positions,gt_positions)
    


def trajectoryFollowingEvaluation(traj_topic, estimation_topic):

    se_positions   = np.array([ estimation_topic.getSyncData(getXpose),
                                estimation_topic.getSyncData(getYpose),
                                estimation_topic.getSyncData(getZpose)])
                                
    traj_positions = np.array([ traj_topic.getSyncData(lambda x: x.positions[0]),
                                traj_topic.getSyncData(lambda x: x.positions[1]),
                                traj_topic.getSyncData(lambda x: x.positions[2])])
    
    time = traj_topic.getSyncTime()
    
    # find landing end
    end_index = -1
    for i, z in enumerate(traj_positions[2,:]):
        if z < -0.01:
            end_index = i
            print("Time cropped to landing at T=", time[end_index],' s')
            break 
    
    se_positions = se_positions[:,0:end_index]
    traj_positions = traj_positions[:,0:end_index]
    time = time[0:end_index]
    
    y_labels = ['x (m)','y (m)','z (m)']
    fig1 = plot3Subplots1perAxis(traj_positions,se_positions,time,
                            x_axis_label="time(s)",
                            y_axis_labels=y_labels,
                            title="Trajectory following",
                            line_1_label="traj",
                            line_2_label="estimation")

    fig2 = plot2lines3D(traj_positions,se_positions)
    
    plotErrorPerAxis(   traj_positions,se_positions,time,
                        x_axis_label="time(s)",
                        y_axis_label="error(m)",
                        title= "Trajectory following error",
                        line_labels=["x_error","y_error","z_error"])
    
    plotTotalError(     traj_positions,se_positions,time,
                        x_axis_label="time(s)",
                        y_axis_label="error(m)",
                        title= "Trajectory following error",
                        line_label=["error"])
    
    

    print("TRAJECTORY FOLLOWING ERROR")
    axesbyaxesRMSE(se_positions,traj_positions)
    error, dists = Calculate3Derror(se_positions,traj_positions)


 

def SpeedAnalysis(traj_topic, estimation_topic):

    se_speeds   = np.array([    estimation_topic.getSyncData(getXspeed),
                                estimation_topic.getSyncData(getYspeed),
                                estimation_topic.getSyncData(getZspeed)])
                                
    traj_speeds = np.array([    traj_topic.getSyncData(lambda x: x.velocities[0]),
                                traj_topic.getSyncData(lambda x: x.velocities[1]),
                                traj_topic.getSyncData(lambda x: x.velocities[2])])
    
    traj_pose_add = traj_topic.getSyncData(lambda x: x.positions[2])
    time = traj_topic.getSyncTime()
    
    # find landing end
    end_index = -1
    for i, z in enumerate(traj_pose_add):
        if z < -0.01:
            end_index = i
            print("Time cropped to landing at T=", time[end_index],' s')
            break 
    
    
    #find start run time 
    begin_index = 0
    for i, v_x in enumerate(traj_speeds[0,:]):
        if abs(v_x) > + 0.01:
            begin_index = i
            print("Time begins to fly at T=", time[begin_index],' s')
            break 
    
    

    
    se_speeds = se_speeds[:,begin_index:end_index]
    traj_speeds = traj_speeds[:,begin_index:end_index]
    time = time[begin_index:end_index]

    
    y_labels = ['v_x (m/s)','v_x (m/s)','v_z (m/s)']
    fig1 = plot3Subplots1perAxis(traj_speeds,se_speeds,time,
                            x_axis_label="time(s)",
                            y_axis_labels=y_labels,
                            title="Speed trajectory following",
                            line_1_label="traj",
                            line_2_label="estimation")

    
    print("SPEED ANALYSIS ERROR")
    axesbyaxesRMSE(traj_speeds,se_speeds,True)
    error, dists = Calculate3Derror(se_speeds,traj_speeds,True)
  

    #find end run time 
    end_run_index = -1
    counter = 0
    for i, v_x in enumerate(traj_speeds[0,:]):
        if v_x == 0.0:
            counter += 1
            if counter > 10:
                end_run_index = i
                print("Time end to fly at T=", time[end_run_index],' s')
                break
        else:
            counter = 0
    
    run_speeds = se_speeds[:,:end_run_index]
    run_times  = time[:end_run_index]
    speeds = np.sqrt(np.power(run_speeds[0,:],2)+ np.power(run_speeds[2,:],2) +np.power(run_speeds[2,:],2))
   
    print("\t MAX SPEED = ",np.max(speeds), ' m/s')
    print("\t AVG SPEED = ",np.average(speeds), ' m/s')
    print("\t Elapsed time = ",run_times[-1]-run_times[0], 's')
    
    

    fig,ax =plt.subplots()
    fig.suptitle('run measured speed', fontsize=12)
    ax.plot(run_times,speeds,label='speed')
    ax.set_xlabel('time (s)')
    ax.set_ylabel('speed (m/s)')
    ax.grid(True)


    







