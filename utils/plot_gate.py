#!/usr/bin/python3
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np

def plot_gate(gate_poses, ax):

    # gate dimensions
    w = 1.0
    a = 0.2
    h = 1.0 
    color = 'gray'

    x, y, z = [], [], []
    for gate in gate_poses:
        c_x = gate[0]
        c_y = gate[1]
        c_z = gate[2]
        c_yaw = gate[3]

        x_lim_int = [c_x + w/2*np.sin(c_yaw), c_x - w/2*np.sin(c_yaw)]
        y_lim_int = [c_y + w/2*np.cos(c_yaw), c_y - w/2*np.cos(c_yaw)]
        z_lim_int = [c_z - h/2, c_z + h/2]
        x_lim_ext = [c_x + (w/2 + a)*np.sin(c_yaw), c_x - (w/2 + a)*np.sin(c_yaw)]
        y_lim_ext = [c_y + (w/2 + a)*np.cos(c_yaw), c_y - (w/2 + a)*np.cos(c_yaw)]
        z_lim_ext = [c_z - h/2 - a, c_z + h/2 + a]

        # top
        x.append([x_lim_ext[0], x_lim_ext[1], x_lim_ext[1], x_lim_ext[0]])
        y.append([y_lim_ext[0], y_lim_ext[1], y_lim_ext[1], y_lim_ext[0]])
        z.append([z_lim_int[1], z_lim_int[1], z_lim_ext[1], z_lim_ext[1]])
        # bottom
        x.append([x_lim_ext[0], x_lim_ext[1], x_lim_ext[1], x_lim_ext[0]])
        y.append([y_lim_ext[0], y_lim_ext[1], y_lim_ext[1], y_lim_ext[0]])
        z.append([z_lim_int[0], z_lim_int[0], z_lim_ext[0], z_lim_ext[0]])
        # left
        x.append([x_lim_ext[0], x_lim_ext[0], x_lim_int[0], x_lim_int[0]])
        y.append([y_lim_ext[0], y_lim_ext[0], y_lim_int[0], y_lim_int[0]])
        z.append([z_lim_ext[0], z_lim_ext[1], z_lim_int[1], z_lim_int[0]])
        # right
        x.append([x_lim_ext[1], x_lim_ext[1], x_lim_int[1], x_lim_int[1]])
        y.append([y_lim_ext[1], y_lim_ext[1], y_lim_int[1], y_lim_int[1]])
        z.append([z_lim_ext[0], z_lim_ext[1], z_lim_int[1], z_lim_int[0]])
        # inside
        # x.append([x_lim_int[0], x_lim_int[1], x_lim_int[1], x_lim_int[0]])
        # y.append([y_lim_int[0], y_lim_int[1], y_lim_int[1], y_lim_int[0]])
        # z.append([z_lim_int[0], z_lim_int[0], z_lim_int[1], z_lim_int[1]])
    
    surfaces = []
    
    for i in range(len(x)):
        surfaces.append([list(zip(x[i],y[i],z[i]))])
    
    for surface in surfaces:
        poly = Poly3DCollection(surface, color=color, alpha=0.5)
        ax.add_collection3d(poly)

