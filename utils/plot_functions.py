import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

from utils.ros2_utils import extract_3d_vector 

from utils.plot_gate import plot_gate

def convert_into_plottable_data(topic_data):
    data = [extract_3d_vector(msg) for msg in topic_data]
    # Extract the data
    x_data = [x[0] for x in data]
    y_data = [x[1] for x in data]
    z_data = [x[2] for x in data]
    return [x_data, y_data, z_data]


def plot3Subplots1perAxis(line1,line2,time, x_axis_label, y_axis_labels,title, line_1_label=None,line_2_label=None):

    fig, axes = plt.subplots(3, 1, sharex=True)

    fig.suptitle(title, fontsize=12)

    for i in range(3):
        axes[i].plot(time,line1[i],label= line_1_label)
        axes[i].plot(time,line2[i],label= line_2_label)
        axes[i].grid(True)
        axes[i].set_ylabel(y_axis_labels[i])
        axes[i].legend()
        
    axes[-1].set_xlabel(x_axis_label)
    return fig


def plotErrorPerAxis(line1,line2,time, x_axis_label, y_axis_label,title, line_labels=None):

    fig, axes = plt.subplots()

    fig.suptitle(title, fontsize=12)

    for i in range(3):
        axes.plot(time,line1[i]-line2[i],label =line_labels[i])

    axes.set_xlabel(x_axis_label)
    axes.set_ylabel(y_axis_label)
    axes.legend()    
    axes.grid(True)
        
    return fig

def plotTotalError(line1,line2,time, x_axis_label, y_axis_label,title, line_label=None):

    fig, axes = plt.subplots()

    fig.suptitle(title, fontsize=12)

    dists = np.sqrt(np.sum(np.power(line1- line2,2),axis=0))
    
    axes.plot(time,dists, label =line_label[0])

    axes.set_xlabel(x_axis_label)
    axes.set_ylabel(y_axis_label)
    # axes.legend()    
    axes.grid(True)
        
    return fig


def plot3Dlines(lines,projection= None , x_lims= None,y_lims= None,z_lims= None , labels=None):
    fig = plt.figure()
    axes = plt.axes(projection='3d')
    if projection is not None:
        if len(projection) != 4:
            raise AssertionError("projection must be a 4 elem list (x,y,z,scale)")
        axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag(projection)) 

    axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes),np.diag([1,1,1,1])) 

    for i, line in enumerate(lines):
        if labels:
            label = labels[i]
        else:
            label = None
        axes.plot(line[0],line[1],line[2],label = label )


    GATES = [[1.44, 0.24, 2.03, 1.57], 
             [-0.5, 0.2, 1.91, 1.57]]
    
    plot_gate(GATES, axes)
    x_lims = [-2,2.5]
    y_lims = [-1.5,2]
    z_lims = [0,2.5]
    
    if x_lims:
        axes.set_xlim3d(x_lims)
    if y_lims:
        axes.set_ylim3d(y_lims)
    y_lims = [-1,2]
    if z_lims:
        axes.set_zlim3d(z_lims)
    # else:
    #     if np.max(np.abs(line2[1,:])) < 1:
    #         axes.set_ylim3d(-1,1)
    # if y_lims :
    #     axes.set_zlim3d(z_lims)

    # y_tick = np.linspace(y_lims[0],y_lims[1],5)
    y_tick = np.arange(y_lims[0],y_lims[1],1)
    # add last element
    y_tick = list(y_tick)
    y_tick.append(y_lims[1])
    axes.set_yticks(y_tick)
    axes.view_init(elev=45, azim=-45)
    
    axes.legend()
    return axes
    
    
    
    
