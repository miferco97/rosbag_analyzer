import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

from utils.ros2_utils import extract_3d_vector 

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


def add_noise_to_data(data, noise_level=0.015):
    #data is a list of 3 lists each containing the x,y,z data
    noisy_data = []
    for axis in data:
        axis_data = []
        noisy_value = axis[0] + np.random.normal(0, noise_level)
        for i , value in enumerate(axis):
            if i == 0:
                axis_data.append(noisy_value)
                continue
            diff = value - axis[i-1]
            noisy_value = axis_data[-1] + diff + np.random.normal(0, noise_level)


            axis_data.append(noisy_value)
            # axis_data.append(value + np.random.normal(0, noise_level))

        noisy_data.append(axis_data)

    return noisy_data

def rotate_point(x, y, z, angle, axis='z'):
    """
    Rotate a point around the specified axis by a given angle.

    Parameters:
    - x, y, z: Coordinates of the point
    - angle: Rotation angle in degrees
    - axis: The axis around which to rotate ('x', 'y', or 'z')

    Returns:
    - x_rot, y_rot, z_rot: Rotated coordinates
    """
    # Convert angle from degrees to radians
    theta = np.radians(angle)

    # Define rotation matrices for each axis
    if axis == 'x':
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta),  np.cos(theta)]
        ])
    elif axis == 'y':
        rotation_matrix = np.array([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])
    elif axis == 'z':
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0, 0, 1]
        ])
    else:
        raise ValueError("Axis must be 'x', 'y', or 'z'")
     # Original coordinates as a vector
    point = np.array([x, y, z])

    # Apply the rotation matrix
    rotated_point = np.dot(rotation_matrix, point)

    # Return the rotated coordinates
    return rotated_point[0], rotated_point[1], rotated_point[2]

def rotate_line(line, angle, axis='z'):
    """
    Rotate a line around the specified axis by a given angle.

    Parameters:
    - line: A list of 3 lists, each containing the x, y, and z coordinates of the line
    - angle: Rotation angle in degrees
    - axis: The axis around which to rotate ('x', 'y', or 'z')

    Returns:
    - rotated_line: The rotated line
    """
    # Initialize an empty list to store the rotated line
    rotated_line = []
    len_line = len(line[0])


    x_rot_line = []
    y_rot_line = []
    z_rot_line = []
    # Rotate each point in the line
    for i in range(len(line[0])):
        x, y, z = line[0][i], line[1][i], line[2][i]
        x_rot, y_rot, z_rot = rotate_point(x, y, z, angle, axis)
        x_rot_line.append(x_rot)
        y_rot_line.append(y_rot)
        z_rot_line.append(z_rot)

    rotated_line.append(x_rot_line)
    rotated_line.append(y_rot_line)
    rotated_line.append(z_rot_line)
    
    # test lines are the same length
    assert len_line == len(rotated_line[0])

    return rotated_line


def plot3DlinesBIS(lines,projection= None , x_lims= None,y_lims= None,z_lims= None , labels=None, colors=None):
    # Add gaussian noise to the data to make it more realistic and plot both the noisy and the clean data
    lines_bis = []
    for line in lines:
        line = rotate_line(line, 45, 'z')
        lines_bis.append(line )
        lines_bis.append(add_noise_to_data(line))
    if labels:
        labels_bis = []
        for label in labels:
            labels_bis.append(label +  '')
            labels_bis.append(label + 'Noisy')
    else:
        labels_bis = None
    if colors:
        colors_bis = []
        for color in colors:
            colors_bis.append(color)
            colors_bis.append(color + '--')
    else:
        colors_bis = None

    # z_lims = [-20,25]
    # x_lims = [-28,6]
    # y_lims = [-90,100]

    return plot3Dlines(lines_bis,projection=projection,x_lims=x_lims,y_lims=y_lims,z_lims=z_lims,labels=labels_bis,colors=colors_bis)



def plot3Dlines(lines,projection= None , x_lims= None,y_lims= None,z_lims= None , labels=None, colors=None):
    fig = plt.figure()
    axes = plt.axes(projection='3d')
    if projection is not None:
        if len(projection) != 4:
            raise AssertionError("projection must be a 4 elem list (x,y,z,scale)")
        # axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag(projection)) 
    # axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag([0.2, 1, 0.2, 1]))
        axes.get_proj = lambda: np.dot(Axes3D.get_proj(axes), np.diag([1, 1, 1, 1]))
    for i, line in enumerate(lines):
        if labels:
            label = labels[i]
        else:
            label = None
        if colors:
            color = colors[i]
        else:
            color = None
        axes.plot(line[0],line[1],line[2],color, label = label)
    
    if x_lims:
        axes.set_xlim3d(x_lims)
    if y_lims:
        axes.set_ylim3d(y_lims)
    # axes.set_zticklabels([])

    # axes.view_init(elev=30, azim=0)

    # if z_lims:
    #     axes.set_zlim3d(z_lims)
    # else:
    #     if np.max(np.abs(line2[1,:])) < 1:
    #         axes.set_ylim3d(-1,1)
    # if y_lims :
    #     axes.set_zlim3d(z_lims)
    
    # axes.legend()
    # axes.legend(loc='upper right', ncol=2)

    return axes
    
    
    
    
