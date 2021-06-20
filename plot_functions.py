import matplotlib.pyplot as plt

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

import numpy as np


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
    axes.legend()    
    axes.grid(True)
        
    return fig


def plot2lines3D(line1,line2, projection= None , x_lims= None,y_lims= None,z_lims= None , label1=None ,label2=None):
    fig = plt.figure()
    axes = plt.axes(projection='3d')
    if projection is not None:
        if len(projection) != 4:
            raise AssertionError("projection must be a 4 elem list (x,y,z,scale)")
        axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag(projection)) 
    axes.plot(line1[0],line1[1],line1[2],label = label1 )
    axes.plot(line2[0],line2[1],line2[2],label = label2 )
    
    if x_lims :
        axes.set_xlim3d(x_lims)
    if y_lims :
        axes.set_ylim3d(y_lims)
    else:
        if np.max(np.abs(line2[1,:])) < 1:
            axes.set_ylim3d(-1,1)
    if y_lims :
        axes.set_zlim3d(z_lims)
    
    return axes
    
    
    